# Dataset for contrastive training: loads (problem, positive, negatives) tuples.
from __future__ import annotations

import json
import logging
import random
from pathlib import Path

from torch.utils.data import Dataset

from .data_types import (
    Action,
    ActionType,
    Diagnostic,
    DiagnosticSeverity,
    SearchState,
    TrainingCandidate,
    TrainingExample,
)

log = logging.getLogger(__name__)


class ContrastiveDataset(Dataset):
    """Dataset of (problem, positive_candidate, negative_candidates) tuples.

    Supports two data sources:
      1. **JSONL files** where each line has the schema below.
      2. **Synthetic generation** from a list of (problem, solution) pairs
         and a perturbation function that creates hard negatives.

    JSONL schema::

        {
            "problem": "Write a function that ...",
            "positive": {
                "code": "def foo(): ...",
                "value_target": 0.0,
                "error_category": null
            },
            "negatives": [
                {
                    "code": "def foo(): ...",
                    "diagnostics": ["SyntaxError: ..."],
                    "value_target": 5.0,
                    "error_category": "syntax"
                },
                ...
            ]
        }
    """

    def __init__(
        self,
        data_path: str | None = None,
        examples: list[TrainingExample] | None = None,
        num_negatives: int = 7,
    ):
        self.num_negatives = num_negatives
        if examples is not None:
            self.examples = examples
        elif data_path is not None:
            self.examples = self._load_jsonl(data_path)
        else:
            self.examples = []
            log.warning("ContrastiveDataset created with no data.")

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> dict:
        ex = self.examples[idx]
        # Subsample negatives to fixed count
        negatives = ex.negatives
        if len(negatives) > self.num_negatives:
            negatives = random.sample(negatives, self.num_negatives)
        elif len(negatives) < self.num_negatives:
            # Pad by repeating (with noise if desired)
            while len(negatives) < self.num_negatives:
                negatives.append(random.choice(ex.negatives))
        return {
            "problem": ex.problem,
            "positive": ex.positive,
            "negatives": negatives,
        }

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_jsonl(self, path: str) -> list[TrainingExample]:
        data_path = Path(path)
        if not data_path.exists():
            log.error("Data file not found: %s", path)
            return []

        examples: list[TrainingExample] = []
        with open(data_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                examples.append(self._parse_example(obj))
        log.info("Loaded %d training examples from %s", len(examples), path)
        return examples

    @staticmethod
    def _parse_example(obj: dict) -> TrainingExample:
        problem = obj["problem"]

        def _parse_candidate(d: dict, is_pos: bool) -> TrainingCandidate:
            code = d.get("code", "")
            diags = [
                Diagnostic(message=m, severity=DiagnosticSeverity.ERROR)
                for m in d.get("diagnostics", [])
            ]
            state = SearchState(
                problem=problem,
                code_or_proof=code,
                diagnostics=diags,
            )
            return TrainingCandidate(
                state=state,
                action=Action(text=code, action_type=ActionType.EDIT),
                is_positive=is_pos,
                value_target=d.get("value_target"),
                error_category=d.get("error_category"),
            )

        positive = _parse_candidate(obj["positive"], is_pos=True)
        negatives = [_parse_candidate(n, is_pos=False) for n in obj.get("negatives", [])]
        return TrainingExample(problem=problem, positive=positive, negatives=negatives)


# ---------------------------------------------------------------------------
# Synthetic data generation helpers
# ---------------------------------------------------------------------------


def create_synthetic_negatives(
    problem: str,
    solution: str,
    perturbations: list[str],
    test_code: str = "",
) -> TrainingExample:
    """Create a TrainingExample from a known-good solution and a list of broken variants.

    This is useful for bootstrapping training data before running the full
    proposal → search → collect pipeline.
    """
    positive = TrainingCandidate(
        state=SearchState(problem=problem, code_or_proof=solution),
        action=Action(text=solution),
        is_positive=True,
        value_target=0.0,
        error_category=None,
    )
    negatives: list[TrainingCandidate] = []
    for perturbed in perturbations:
        # Quick syntax check to auto-label
        error_cat: str | None = None
        diags: list[Diagnostic] = []
        try:
            compile(perturbed, "<neg>", "exec")
        except SyntaxError as e:
            error_cat = "syntax"
            diags.append(
                Diagnostic(
                    message=str(e),
                    severity=DiagnosticSeverity.ERROR,
                    category="syntax",
                )
            )
        negatives.append(
            TrainingCandidate(
                state=SearchState(
                    problem=problem,
                    code_or_proof=perturbed,
                    diagnostics=diags,
                ),
                action=Action(text=perturbed),
                is_positive=False,
                value_target=None,
                error_category=error_cat,
            )
        )
    return TrainingExample(problem=problem, positive=positive, negatives=negatives)
