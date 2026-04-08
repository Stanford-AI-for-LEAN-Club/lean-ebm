# Tool adapters: execute actions against compilers, test harnesses, and Lean 4.
from __future__ import annotations

import logging
import subprocess
import tempfile
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path

from .data_types import (
    Action,
    Diagnostic,
    DiagnosticSeverity,
    SearchState,
)

log = logging.getLogger(__name__)


class ToolAdapter(ABC):
    """Abstract interface for executing an action and returning a new state."""

    @abstractmethod
    def execute(
        self, state: SearchState, action: Action
    ) -> tuple[SearchState, bool]:
        """Apply *action* to *state* and return (new_state, is_valid).

        Hard constraints (syntax errors, type errors, kernel failures) should
        set ``is_valid=False`` so the search prunes them immediately.
        """
        ...


# ---------------------------------------------------------------------------
# Python code execution adapter
# ---------------------------------------------------------------------------


class PythonToolAdapter(ToolAdapter):
    """Compiles and optionally runs Python code, returning diagnostics.

    Workflow per action:
      1. Merge action text into the current code (replace or append).
      2. Syntax-check via ``compile()``.
      3. Optionally run a test harness if ``test_code`` is provided in the state
         metadata.
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def execute(
        self, state: SearchState, action: Action
    ) -> tuple[SearchState, bool]:
        new_code = action.text  # For V1, action *is* the full replacement code.
        diagnostics: list[Diagnostic] = []

        # --- Step 1: Syntax check -----------------------------------------
        try:
            compile(new_code, "<candidate>", "exec")
        except SyntaxError as e:
            diagnostics.append(
                Diagnostic(
                    message=f"SyntaxError: {e.msg} (line {e.lineno})",
                    severity=DiagnosticSeverity.ERROR,
                    line=e.lineno,
                    category="syntax",
                )
            )
            new_state = SearchState(
                problem=state.problem,
                code_or_proof=new_code,
                diagnostics=diagnostics,
                history=[*state.history, action.text[:80]],
                metadata=state.metadata,
            )
            return new_state, False  # Hard constraint: prune invalid syntax

        # --- Step 2: Run tests if available -------------------------------
        test_code = state.metadata.get("test_code", "")
        if test_code:
            full_code = new_code + "\n\n" + test_code
            ok, output = self._run_code(full_code)
            if not ok:
                diagnostics.append(
                    Diagnostic(
                        message=output[:500],
                        severity=DiagnosticSeverity.ERROR,
                        category="test_fail",
                    )
                )
            else:
                diagnostics.append(
                    Diagnostic(
                        message="All tests passed.",
                        severity=DiagnosticSeverity.INFO,
                        category="test_pass",
                    )
                )
        else:
            # No tests — just run and capture any runtime errors
            ok, output = self._run_code(new_code)
            if not ok:
                diagnostics.append(
                    Diagnostic(
                        message=output[:500],
                        severity=DiagnosticSeverity.ERROR,
                        category="runtime",
                    )
                )

        new_state = SearchState(
            problem=state.problem,
            code_or_proof=new_code,
            diagnostics=diagnostics,
            history=[*state.history, action.text[:80]],
            metadata=state.metadata,
        )
        # Valid if no error-level diagnostics (soft errors are fine)
        is_valid = not any(
            d.severity == DiagnosticSeverity.ERROR and d.category == "syntax"
            for d in diagnostics
        )
        return new_state, is_valid

    def _run_code(self, code: str) -> tuple[bool, str]:
        """Execute Python code in a subprocess and return (success, output)."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            f.flush()
            try:
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                if result.returncode != 0:
                    return False, result.stderr.strip()
                return True, result.stdout.strip()
            except subprocess.TimeoutExpired:
                return False, f"Timeout after {self.timeout}s"
            except Exception as e:
                return False, str(e)
            finally:
                Path(f.name).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Lean 4 tool adapter (scaffold — requires LeanDojo or pantograph)
# ---------------------------------------------------------------------------


class LeanToolAdapter(ToolAdapter):
    """Adapter for Lean 4 tactic execution.

    This is a scaffold.  A full implementation would use LeanDojo or
    PyPantograph to:
      1. Send a tactic to the Lean kernel.
      2. Collect the new goal state / error.
      3. Return diagnostics with elaboration status.
    """

    def __init__(
        self,
        lean_project_path: str = "",
        timeout: int = 60,
    ):
        self.lean_project_path = lean_project_path
        self.timeout = timeout
        log.warning(
            "LeanToolAdapter is a scaffold. Install LeanDojo or pantograph "
            "for real Lean 4 interaction."
        )

    def execute(
        self, state: SearchState, action: Action
    ) -> tuple[SearchState, bool]:
        # Append tactic to proof text
        new_proof = state.code_or_proof
        if new_proof and not new_proof.endswith("\n"):
            new_proof += "\n"
        new_proof += f"  {action.text}"

        # TODO: Call Lean kernel via LeanDojo / pantograph
        # For now, always return as "valid" with a placeholder diagnostic.
        diagnostics = [
            Diagnostic(
                message="[scaffold] tactic accepted (no real Lean check)",
                severity=DiagnosticSeverity.WARNING,
                category="scaffold",
            )
        ]

        new_state = SearchState(
            problem=state.problem,
            code_or_proof=new_proof,
            diagnostics=diagnostics,
            history=[*state.history, action.text[:80]],
            goals=state.goals,  # Would be updated by real Lean interaction
            metadata=state.metadata,
        )
        return new_state, True


def build_tool(tool_type: str, **kwargs) -> ToolAdapter:
    """Factory for tool adapters."""
    if tool_type == "python":
        return PythonToolAdapter(**kwargs)
    elif tool_type == "lean":
        return LeanToolAdapter(**kwargs)
    else:
        raise ValueError(f"Unknown tool type: {tool_type}")
