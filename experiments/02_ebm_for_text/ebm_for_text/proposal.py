# Proposal model wrapper: generates K candidate actions from a pretrained causal LM.
from __future__ import annotations

import logging
from dataclasses import dataclass

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .data_types import Action, ActionType, SearchState

log = logging.getLogger(__name__)


@dataclass
class ProposalConfig:
    model_name: str = "Salesforce/codegen-350M-mono"
    max_new_tokens: int = 256
    temperature: float = 0.8
    top_k: int = 50
    top_p: float = 0.95
    num_candidates: int = 8
    device: str = "cpu"
    load_in_8bit: bool = False


class ProposalModel:
    """Wraps a causal LM to serve as the proposal distribution q_φ(a | s, R).

    Given a search state and retrieved context, generates K candidate actions
    via temperature sampling.
    """

    # Prompt templates --------------------------------------------------

    CODE_PROMPT = (
        "### Task\n{problem}\n\n"
        "### Current Code\n```python\n{code}\n```\n\n"
        "{diag_section}"
        "{context_section}"
        "### Next Edit\nWrite the corrected or improved code:\n```python\n"
    )

    LEAN_PROMPT = (
        "### Theorem\n{problem}\n\n"
        "### Current Proof State\n{code}\n\n"
        "{diag_section}"
        "{context_section}"
        "### Next Tactic\n"
    )

    def __init__(self, cfg: ProposalConfig):
        self.cfg = cfg
        log.info("Loading proposal model: %s", cfg.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
        load_kwargs: dict = {}
        if cfg.load_in_8bit:
            load_kwargs["load_in_8bit"] = True
            load_kwargs["device_map"] = "auto"
        else:
            load_kwargs["torch_dtype"] = torch.float16

        self.model = AutoModelForCausalLM.from_pretrained(
            cfg.model_name, **load_kwargs
        )
        if not cfg.load_in_8bit:
            self.model.to(cfg.device)
        self.model.eval()

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        state: SearchState,
        context: str = "",
        mode: str = "code",
    ) -> str:
        diag_section = ""
        if state.diagnostics:
            diag_lines = "\n".join(f"- {d.message}" for d in state.diagnostics[:5])
            diag_section = f"### Diagnostics\n{diag_lines}\n\n"

        context_section = ""
        if context:
            context_section = f"### Retrieved Context\n{context}\n\n"

        template = self.CODE_PROMPT if mode == "code" else self.LEAN_PROMPT
        return template.format(
            problem=state.problem,
            code=state.code_or_proof,
            diag_section=diag_section,
            context_section=context_section,
        )

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    @torch.no_grad()
    def generate_candidates(
        self,
        state: SearchState,
        context: str = "",
        mode: str = "code",
        num_candidates: int | None = None,
    ) -> list[Action]:
        """Sample K candidate actions from the proposal LM.

        Returns a list of Action objects.  Duplicates are deduplicated.
        """
        K = num_candidates or self.cfg.num_candidates
        prompt = self._build_prompt(state, context, mode)
        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=1024
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.cfg.max_new_tokens,
            temperature=self.cfg.temperature,
            top_k=self.cfg.top_k,
            top_p=self.cfg.top_p,
            do_sample=True,
            num_return_sequences=K,
            pad_token_id=self.tokenizer.pad_token_id,
        )

        # Decode only the new tokens
        prompt_len = inputs["input_ids"].shape[1]
        candidates: list[Action] = []
        seen: set[str] = set()
        action_type = ActionType.TACTIC if mode == "lean" else ActionType.EDIT

        for seq in outputs:
            text = self.tokenizer.decode(seq[prompt_len:], skip_special_tokens=True)
            # Trim at code-fence close for code mode
            if mode == "code" and "```" in text:
                text = text[: text.index("```")]
            text = text.strip()
            if text and text not in seen:
                seen.add(text)
                candidates.append(Action(text=text, action_type=action_type))

        return candidates
