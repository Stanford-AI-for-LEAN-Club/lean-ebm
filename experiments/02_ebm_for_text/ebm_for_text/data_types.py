# Core dataclasses for the EBM-for-text search and training pipeline.
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    """Type of action the proposal model can generate."""
    EDIT = "edit"           # Code edit / patch
    TACTIC = "tactic"       # Lean 4 tactic step
    SUBGOAL = "subgoal"     # Subgoal decomposition


class DiagnosticSeverity(str, Enum):
    """Severity of a tool diagnostic."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Diagnostic:
    """A single diagnostic message from a tool (compiler, tests, Lean verifier)."""
    message: str
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR
    line: int | None = None
    category: str = ""  # e.g. "syntax", "type", "test_fail", "elaboration"


@dataclass
class SearchState:
    """A single state in the search tree.

    For code tasks: current source code + test/compiler diagnostics.
    For Lean tasks: current proof state (goals, hypotheses, tactic history).
    """
    problem: str                                # Problem / task description
    code_or_proof: str = ""                     # Current code or proof text
    diagnostics: list[Diagnostic] = field(default_factory=list)
    history: list[str] = field(default_factory=list)  # Tactic / edit history
    goals: list[str] = field(default_factory=list)    # Open goals (Lean)
    metadata: dict = field(default_factory=dict)

    @property
    def is_solved(self) -> bool:
        """Heuristic: solved if no error-level diagnostics remain."""
        return not any(d.severity == DiagnosticSeverity.ERROR for d in self.diagnostics)

    def text_summary(self) -> str:
        """Flat text representation used as energy-model input."""
        parts = [self.code_or_proof]
        if self.diagnostics:
            diag_text = " | ".join(d.message for d in self.diagnostics[:5])
            parts.append(f"[DIAG] {diag_text}")
        if self.goals:
            parts.append(f"[GOALS] {' ; '.join(self.goals[:5])}")
        return "\n".join(parts)


@dataclass
class Action:
    """A single proposed edit, tactic, or subgoal."""
    text: str
    action_type: ActionType = ActionType.EDIT


@dataclass
class SearchNode:
    """A node in the best-first search tree."""
    state: SearchState
    cumulative_energy: float = 0.0
    depth: int = 0
    parent: SearchNode | None = None
    action: Action | None = None          # Action that led to this node

    def __lt__(self, other: SearchNode) -> bool:
        """Lower cumulative energy = higher priority."""
        return self.cumulative_energy < other.cumulative_energy


@dataclass
class TrainingCandidate:
    """A single candidate in a contrastive training example."""
    state: SearchState
    action: Action
    context: str = ""                     # Retrieved context at this step
    is_positive: bool = False
    value_target: float | None = None     # Remaining steps to success (if known)
    error_category: str | None = None     # Error type label for feedback head


@dataclass
class TrainingExample:
    """One training instance: a problem with one positive and N negatives."""
    problem: str
    positive: TrainingCandidate
    negatives: list[TrainingCandidate] = field(default_factory=list)


@dataclass
class SearchResult:
    """Result of a search run."""
    solved: bool
    solution: str = ""
    trajectory: list[tuple[SearchState, Action]] = field(default_factory=list)
    nodes_expanded: int = 0
    best_energy: float = float("inf")
