# Cross-encoder energy model with ranking, value, and feedback heads.
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from .data_types import Action, Diagnostic, SearchState


class EnergyModel(nn.Module):
    """Bidirectional cross-encoder that scores (problem, state, action, context, diagnostics).

    Three output heads:
      - **ranking_head**: scalar energy E(x, τ). Lower energy = better candidate.
      - **value_head**: scalar cost-to-go V(s'). Estimates remaining work.
      - **feedback_head**: logits over error-type categories (teaches *why* code is wrong).
    """

    SPECIAL_TOKENS = {
        "problem": "[PROBLEM]",
        "state": "[STATE]",
        "action": "[ACTION]",
        "context": "[CONTEXT]",
        "diag": "[DIAG]",
        "goals": "[GOALS]",
    }

    def __init__(
        self,
        encoder_name: str = "microsoft/codebert-base",
        hidden_dim: int = 768,
        num_feedback_classes: int = 8,
        max_seq_length: int = 512,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.max_seq_length = max_seq_length
        self.num_feedback_classes = num_feedback_classes

        self.tokenizer = AutoTokenizer.from_pretrained(encoder_name)
        self.encoder = AutoModel.from_pretrained(encoder_name)
        enc_dim = self.encoder.config.hidden_size

        # Three heads on the CLS embedding
        self.ranking_head = nn.Sequential(
            nn.Linear(enc_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )
        self.value_head = nn.Sequential(
            nn.Linear(enc_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )
        self.feedback_head = nn.Sequential(
            nn.Linear(enc_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_feedback_classes),
        )

    # ------------------------------------------------------------------
    # Text formatting
    # ------------------------------------------------------------------

    def format_input(
        self,
        problem: str,
        state: SearchState,
        action: Action,
        context: str = "",
    ) -> str:
        """Build the flat text fed to the cross-encoder."""
        parts = [
            f"{self.SPECIAL_TOKENS['problem']} {problem}",
            f"{self.SPECIAL_TOKENS['state']} {state.text_summary()}",
            f"{self.SPECIAL_TOKENS['action']} {action.text}",
        ]
        if context:
            parts.append(f"{self.SPECIAL_TOKENS['context']} {context}")
        if state.diagnostics:
            diag_text = " | ".join(d.message for d in state.diagnostics[:5])
            parts.append(f"{self.SPECIAL_TOKENS['diag']} {diag_text}")
        if state.goals:
            parts.append(f"{self.SPECIAL_TOKENS['goals']} {' ; '.join(state.goals[:5])}")
        return " ".join(parts)

    def tokenize(
        self,
        texts: list[str],
        device: torch.device | str = "cpu",
    ) -> dict[str, torch.Tensor]:
        """Tokenize a batch of formatted texts."""
        enc = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_seq_length,
            return_tensors="pt",
        )
        return {k: v.to(device) for k, v in enc.items()}

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        **kwargs,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Returns (energy, value, feedback_logits) each of shape (B,) / (B, C)."""
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_emb = outputs.last_hidden_state[:, 0]  # (B, enc_dim)

        energy = self.ranking_head(cls_emb).squeeze(-1)          # (B,)
        value = self.value_head(cls_emb).squeeze(-1)              # (B,)
        feedback_logits = self.feedback_head(cls_emb)             # (B, C)
        return energy, value, feedback_logits

    # ------------------------------------------------------------------
    # Convenience: score a batch of (state, action) pairs
    # ------------------------------------------------------------------

    @torch.no_grad()
    def score(
        self,
        problem: str,
        states: list[SearchState],
        actions: list[Action],
        contexts: list[str] | None = None,
        device: torch.device | str = "cpu",
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Score a batch and return (energies, values).  Used during search."""
        if contexts is None:
            contexts = [""] * len(states)
        texts = [
            self.format_input(problem, s, a, c)
            for s, a, c in zip(states, actions, contexts)
        ]
        tok = self.tokenize(texts, device=device)
        energy, value, _ = self.forward(**tok)
        return energy, value


# ---------------------------------------------------------------------------
# Loss functions
# ---------------------------------------------------------------------------


def contrastive_ranking_loss(
    energy_pos: torch.Tensor,
    energy_neg: torch.Tensor,
) -> torch.Tensor:
    """InfoNCE-style contrastive loss where lower energy = better.

    L = -log( exp(-E_pos) / (exp(-E_pos) + Σ_j exp(-E_neg_j)) )

    Args:
        energy_pos: (B,) energies of positive candidates.
        energy_neg: (B, N) energies of negative candidates.
    """
    # Treat -energy as logit; positive is index 0
    logits = torch.cat([-energy_pos.unsqueeze(1), -energy_neg], dim=1)  # (B, 1+N)
    labels = torch.zeros(logits.shape[0], dtype=torch.long, device=logits.device)
    return F.cross_entropy(logits, labels)


def value_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """MSE on the cost-to-go head."""
    return F.mse_loss(pred, target)


def feedback_loss(logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    """Cross-entropy on the error-type classification head."""
    return F.cross_entropy(logits, labels)
