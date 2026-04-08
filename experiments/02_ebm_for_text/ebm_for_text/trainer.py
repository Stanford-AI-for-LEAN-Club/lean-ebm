# Trainer: contrastive ranking training for the energy model with value and feedback auxiliary losses.
from __future__ import annotations

import logging
import os
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader

from .data_types import Action, SearchState, TrainingCandidate
from .energy_model import (
    EnergyModel,
    contrastive_ranking_loss,
    feedback_loss,
    value_loss,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error-category → integer mapping for feedback head
# ---------------------------------------------------------------------------

ERROR_CATEGORIES: dict[str, int] = {
    "none": 0,
    "syntax": 1,
    "type": 2,
    "runtime": 3,
    "test_fail": 4,
    "elaboration": 5,
    "timeout": 6,
    "other": 7,
}


def category_to_label(cat: str | None) -> int:
    if cat is None:
        return ERROR_CATEGORIES["none"]
    return ERROR_CATEGORIES.get(cat, ERROR_CATEGORIES["other"])


# ---------------------------------------------------------------------------
# Collation helper
# ---------------------------------------------------------------------------


def collate_for_energy_model(
    energy_model: EnergyModel,
    problem: str,
    candidates: list[TrainingCandidate],
    device: torch.device | str,
) -> dict[str, torch.Tensor]:
    """Tokenize a list of candidates into a single batch."""
    texts = [
        energy_model.format_input(
            problem,
            c.state,
            c.action,
            c.context,
        )
        for c in candidates
    ]
    return energy_model.tokenize(texts, device=device)


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------


class EBMTrainer:
    """Trains the energy model with contrastive ranking + auxiliary losses.

    Losses (from §4 of the proposal):
      L_total = w_rank * L_rank + w_value * L_value + w_feedback * L_feedback

    where L_rank is InfoNCE over (positive, negatives), L_value is MSE on the
    cost-to-go head, and L_feedback is cross-entropy on error-type prediction.
    """

    def __init__(
        self,
        energy_model: EnergyModel,
        *,
        learning_rate: float = 1e-5,
        weight_decay: float = 0.01,
        grad_clip: float = 1.0,
        ranking_weight: float = 1.0,
        value_weight: float = 0.5,
        feedback_weight: float = 0.3,
        device: str = "cpu",
        checkpoint_dir: str = "checkpoints",
        save_steps: int = 500,
        log_steps: int = 10,
    ):
        self.energy_model = energy_model.to(device)
        self.device = device
        self.grad_clip = grad_clip
        self.ranking_weight = ranking_weight
        self.value_weight = value_weight
        self.feedback_weight = feedback_weight
        self.checkpoint_dir = Path(checkpoint_dir)
        self.save_steps = save_steps
        self.log_steps = log_steps

        self.optimizer = AdamW(
            energy_model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
        )
        self.global_step = 0

    # ------------------------------------------------------------------
    # Single training step
    # ------------------------------------------------------------------

    def train_step(
        self,
        problem: str,
        positive: TrainingCandidate,
        negatives: list[TrainingCandidate],
    ) -> dict[str, float]:
        """One gradient step on a single (positive, negatives) group."""
        self.energy_model.train()

        all_candidates = [positive] + negatives
        tok = collate_for_energy_model(
            self.energy_model, problem, all_candidates, self.device
        )

        energy, value_pred, fb_logits = self.energy_model(**tok)

        energy_pos = energy[:1]                # (1,)
        energy_neg = energy[1:].unsqueeze(0)   # (1, N)

        # ---- Ranking loss ------------------------------------------------
        loss_rank = contrastive_ranking_loss(energy_pos, energy_neg)

        # ---- Value loss (only if labels available) -----------------------
        loss_val = torch.tensor(0.0, device=self.device)
        value_targets = [
            c.value_target for c in all_candidates if c.value_target is not None
        ]
        if value_targets:
            target_tensor = torch.tensor(
                [c.value_target if c.value_target is not None else 0.0 for c in all_candidates],
                device=self.device,
            )
            mask = torch.tensor(
                [c.value_target is not None for c in all_candidates],
                device=self.device,
            )
            if mask.any():
                loss_val = value_loss(value_pred[mask], target_tensor[mask])

        # ---- Feedback loss (only if labels available) --------------------
        loss_fb = torch.tensor(0.0, device=self.device)
        fb_labels = torch.tensor(
            [category_to_label(c.error_category) for c in all_candidates],
            dtype=torch.long,
            device=self.device,
        )
        has_fb = any(c.error_category is not None for c in all_candidates)
        if has_fb:
            loss_fb = feedback_loss(fb_logits, fb_labels)

        # ---- Total -------------------------------------------------------
        total = (
            self.ranking_weight * loss_rank
            + self.value_weight * loss_val
            + self.feedback_weight * loss_fb
        )

        self.optimizer.zero_grad()
        total.backward()
        nn.utils.clip_grad_norm_(self.energy_model.parameters(), self.grad_clip)
        self.optimizer.step()
        self.global_step += 1

        logs = {
            "loss/total": total.item(),
            "loss/ranking": loss_rank.item(),
            "loss/value": loss_val.item(),
            "loss/feedback": loss_fb.item(),
            "energy/positive": energy_pos.mean().item(),
            "energy/negative": energy_neg.mean().item(),
            "step": self.global_step,
        }

        if self.global_step % self.log_steps == 0:
            log.info(
                "step=%d  loss=%.4f  rank=%.4f  val=%.4f  fb=%.4f  E+=%.3f  E-=%.3f",
                self.global_step,
                logs["loss/total"],
                logs["loss/ranking"],
                logs["loss/value"],
                logs["loss/feedback"],
                logs["energy/positive"],
                logs["energy/negative"],
            )

        if self.save_steps > 0 and self.global_step % self.save_steps == 0:
            self.save_checkpoint()

        return logs

    # ------------------------------------------------------------------
    # Full epoch over a dataset
    # ------------------------------------------------------------------

    def train_epoch(self, dataloader: DataLoader) -> list[dict[str, float]]:
        """Train one epoch over a DataLoader that yields TrainingExample dicts."""
        all_logs: list[dict[str, float]] = []
        for batch in dataloader:
            # DataLoader yields dicts with keys: problem, positive, negatives
            logs = self.train_step(
                problem=batch["problem"],
                positive=batch["positive"],
                negatives=batch["negatives"],
            )
            all_logs.append(logs)
        return all_logs

    def train(self, dataloader: DataLoader, epochs: int = 1) -> None:
        """Full training loop over multiple epochs."""
        for epoch in range(epochs):
            log.info("=== Epoch %d/%d ===", epoch + 1, epochs)
            epoch_logs = self.train_epoch(dataloader)
            avg_loss = sum(l["loss/total"] for l in epoch_logs) / max(len(epoch_logs), 1)
            avg_rank = sum(l["loss/ranking"] for l in epoch_logs) / max(len(epoch_logs), 1)
            log.info(
                "Epoch %d done — avg_loss=%.4f, avg_ranking=%.4f, steps=%d",
                epoch + 1, avg_loss, avg_rank, len(epoch_logs),
            )
        self.save_checkpoint()

    # ------------------------------------------------------------------
    # Checkpointing
    # ------------------------------------------------------------------

    def save_checkpoint(self, path: str | Path | None = None) -> None:
        save_path = Path(path) if path else self.checkpoint_dir / f"step_{self.global_step}.pt"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state_dict": self.energy_model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "global_step": self.global_step,
            },
            save_path,
        )
        log.info("Saved checkpoint to %s", save_path)

    def load_checkpoint(self, path: str | Path) -> None:
        ckpt = torch.load(path, map_location=self.device, weights_only=False)
        self.energy_model.load_state_dict(ckpt["model_state_dict"])
        self.optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        self.global_step = ckpt["global_step"]
        log.info("Loaded checkpoint from %s (step %d)", path, self.global_step)
