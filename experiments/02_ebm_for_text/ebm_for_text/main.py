# Entry point: train the energy model or run best-first search.
from __future__ import annotations

import logging
import sys
from pathlib import Path

import hydra
import torch
from omegaconf import DictConfig, OmegaConf
from torch.utils.data import DataLoader

from .data_types import (
    Action,
    ActionType,
    Diagnostic,
    DiagnosticSeverity,
    SearchState,
    TrainingCandidate,
    TrainingExample,
)
from .dataset import ContrastiveDataset, create_synthetic_negatives
from .energy_model import EnergyModel
from .proposal import ProposalConfig, ProposalModel
from .retrieval import Document, Retriever, RetrievalConfig
from .search import best_first_search
from .tools import build_tool
from .trainer import EBMTrainer

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------


def train(cfg: DictConfig) -> None:
    """Train the energy model with contrastive ranking loss."""
    device = cfg.device

    # 1. Energy model
    energy_model = EnergyModel(
        encoder_name=cfg.energy_model.encoder_name,
        hidden_dim=cfg.energy_model.hidden_dim,
        num_feedback_classes=cfg.energy_model.num_feedback_classes,
        max_seq_length=cfg.energy_model.max_seq_length,
        dropout=cfg.energy_model.dropout,
    )

    # 2. Dataset
    if cfg.training.data_path:
        dataset = ContrastiveDataset(
            data_path=cfg.training.data_path,
            num_negatives=cfg.training.num_negatives,
        )
    else:
        log.info("No data_path provided — using built-in demo examples.")
        dataset = ContrastiveDataset(
            examples=_demo_training_examples(),
            num_negatives=cfg.training.num_negatives,
        )

    # Custom collate: each example is already a dict, pass through
    dataloader = DataLoader(
        dataset,
        batch_size=1,  # process one (pos, neg-group) at a time
        shuffle=True,
        collate_fn=lambda batch: batch[0],  # unwrap single-element batch
    )

    # 3. Trainer
    trainer = EBMTrainer(
        energy_model,
        learning_rate=cfg.training.learning_rate,
        weight_decay=cfg.training.weight_decay,
        grad_clip=cfg.training.grad_clip,
        ranking_weight=cfg.training.ranking_weight,
        value_weight=cfg.training.value_weight,
        feedback_weight=cfg.training.feedback_weight,
        device=device,
        checkpoint_dir=cfg.training.checkpoint_dir,
        save_steps=cfg.training.save_steps,
        log_steps=cfg.training.log_steps,
    )

    # Resume from checkpoint if provided
    if cfg.checkpoint:
        trainer.load_checkpoint(cfg.checkpoint)

    # 4. Train
    log.info("Starting training for %d epochs (%d examples)", cfg.training.epochs, len(dataset))
    trainer.train(dataloader, epochs=cfg.training.epochs)
    log.info("Training complete. Final checkpoint in %s", cfg.training.checkpoint_dir)


# ---------------------------------------------------------------------------
# Search (inference)
# ---------------------------------------------------------------------------


def search(cfg: DictConfig) -> None:
    """Run best-first search on a problem using trained energy model + proposal LM."""
    device = cfg.device

    # 1. Energy model
    energy_model = EnergyModel(
        encoder_name=cfg.energy_model.encoder_name,
        hidden_dim=cfg.energy_model.hidden_dim,
        num_feedback_classes=cfg.energy_model.num_feedback_classes,
        max_seq_length=cfg.energy_model.max_seq_length,
        dropout=cfg.energy_model.dropout,
    )
    if cfg.checkpoint:
        ckpt = torch.load(cfg.checkpoint, map_location=device, weights_only=False)
        energy_model.load_state_dict(ckpt["model_state_dict"])
        log.info("Loaded energy model from %s", cfg.checkpoint)
    energy_model.to(device)
    energy_model.eval()

    # 2. Proposal model
    proposal_cfg = ProposalConfig(
        model_name=cfg.proposal.model_name,
        max_new_tokens=cfg.proposal.max_new_tokens,
        temperature=cfg.proposal.temperature,
        top_k=cfg.proposal.top_k,
        top_p=cfg.proposal.top_p,
        num_candidates=cfg.proposal.num_candidates,
        device=device,
        load_in_8bit=cfg.proposal.load_in_8bit,
    )
    proposal = ProposalModel(proposal_cfg)

    # 3. Tool
    tool_kwargs = {"timeout": cfg.tool.timeout}
    tool = build_tool(cfg.tool.type, **tool_kwargs)

    # 4. Retriever
    retriever = Retriever(RetrievalConfig(
        top_k=cfg.retrieval.top_k,
        max_context_tokens=cfg.retrieval.max_context_tokens,
    ))

    # 5. Demo problem
    problem = "Write a Python function `fibonacci(n)` that returns the n-th Fibonacci number."
    test_code = (
        "assert fibonacci(0) == 0\n"
        "assert fibonacci(1) == 1\n"
        "assert fibonacci(10) == 55\n"
        "print('All tests passed!')\n"
    )
    initial_state = SearchState(
        problem=problem,
        code_or_proof="",
        metadata={"test_code": test_code},
    )

    # 6. Search
    log.info("Starting best-first search ...")
    result = best_first_search(
        problem=problem,
        initial_state=initial_state,
        energy_model=energy_model,
        proposal=proposal,
        tool=tool,
        retriever=retriever,
        budget=cfg.search.budget,
        beam_width=cfg.search.beam_width,
        lambda_value=cfg.search.lambda_value,
        mode=cfg.search.mode,
        device=device,
    )

    print("\n" + "=" * 60)
    print(f"Solved: {result.solved}")
    print(f"Nodes expanded: {result.nodes_expanded}")
    print(f"Best energy: {result.best_energy:.4f}")
    print("=" * 60)
    if result.solution:
        print("Solution:")
        print(result.solution)


# ---------------------------------------------------------------------------
# Demo training data (small built-in set for smoke-testing)
# ---------------------------------------------------------------------------


def _demo_training_examples() -> list[TrainingExample]:
    """A handful of hard-coded examples so training can run without external data."""
    examples = []

    # Example 1: fibonacci
    examples.append(
        create_synthetic_negatives(
            problem="Write a Python function `fibonacci(n)` that returns the n-th Fibonacci number.",
            solution="def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n",
            perturbations=[
                "def fibonacci(n)\n    return n\n",  # syntax error (missing colon)
                "def fibonacci(n):\n    return fibonacci(n-1) + fibonacci(n-2)\n",  # infinite recursion (no base case)
                "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) - fibonacci(n-2)\n",  # wrong operator
                "def fibonacci(n):\n    a, b = 1, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n",  # off-by-one
                "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)\n",  # wrong function name
                "def fibonacci(n):\n    return n * (n + 1) // 2\n",  # wrong formula entirely
                "def fibonacci(n):\n    if n == 0:\n        return 0\n    return n\n",  # trivial wrong
            ],
        )
    )

    # Example 2: factorial
    examples.append(
        create_synthetic_negatives(
            problem="Write a Python function `factorial(n)` that returns n!.",
            solution="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n",
            perturbations=[
                "def factorial(n):\n    return n * factorial(n)\n",  # infinite recursion
                "def factorial(n)\n    return 1\n",  # syntax error
                "def factorial(n):\n    if n <= 1:\n        return 0\n    return n * factorial(n - 1)\n",  # wrong base case
                "def factorial(n):\n    result = 0\n    for i in range(1, n+1):\n        result *= i\n    return result\n",  # starts at 0
                "def factorial(n):\n    return n ** n\n",  # wrong formula
                "def factorial(n):\n    if n <= 1:\n        return 1\n    return n + factorial(n - 1)\n",  # + instead of *
                "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n",  # wrong name
            ],
        )
    )

    # Example 3: is_palindrome
    examples.append(
        create_synthetic_negatives(
            problem="Write a Python function `is_palindrome(s)` that returns True if s is a palindrome.",
            solution='def is_palindrome(s):\n    return s == s[::-1]\n',
            perturbations=[
                'def is_palindrome(s):\n    return s == s[::1]\n',  # not reversed
                'def is_palindrome(s)\n    return s == s[::-1]\n',  # syntax error
                'def is_palindrome(s):\n    return s != s[::-1]\n',  # negated
                'def is_palindrome(s):\n    return len(s) == len(s[::-1])\n',  # always true
                'def is_palindrome(s):\n    return s == reversed(s)\n',  # type mismatch
                'def palindrome(s):\n    return s == s[::-1]\n',  # wrong name
                'def is_palindrome(s):\n    for i in range(len(s)):\n        if s[i] != s[i]:\n            return False\n    return True\n',  # comparing to self
            ],
        )
    )

    return examples


# ---------------------------------------------------------------------------
# Hydra entry point
# ---------------------------------------------------------------------------


@hydra.main(config_path="../config", config_name="ebm_text", version_base=None)
def main(cfg: DictConfig) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log.info("Config:\n%s", OmegaConf.to_yaml(cfg))

    if cfg.mode == "train":
        train(cfg)
    elif cfg.mode == "search":
        search(cfg)
    else:
        log.error("Unknown mode: %s (expected 'train' or 'search')", cfg.mode)
        sys.exit(1)


if __name__ == "__main__":
    main()
