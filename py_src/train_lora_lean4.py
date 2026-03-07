"""
LoRA fine-tuning of Goedel-Prover-V2-32B on MiniF2F-Lean4.

Train on validation split, evaluate on test split.
Usage:
    CUDA_VISIBLE_DEVICES=6 uv run python -m lean_ebm.train_lora_lean4
"""

import argparse
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig
from trl import SFTTrainer

def parse_args():
    parser = argparse.ArgumentParser(description="LoRA fine-tune Goedel-Prover-V2-32B on MiniF2F-Lean4")
    parser.add_argument("--model_name", type=str, default="Goedel-LM/Goedel-Prover-V2-32B")
    parser.add_argument("--dataset_name", type=str, default="brando/minif2f-lean4")
    parser.add_argument("--output_dir", type=str, default="experiments/00_lm_mini_f2f/checkpoints")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--grad_accum", type=int, default=4)
    parser.add_argument("--max_seq_length", type=int, default=2048)
    parser.add_argument("--lora_r", type=int, default=16)
    parser.add_argument("--lora_alpha", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


SYSTEM_PROMPT = "You are a Lean 4 theorem prover. Given a formal Lean 4 theorem statement, provide a proof."


def format_example(example, tokenizer):
    """Format a single example as chat messages for causal LM training."""
    user_msg = f"Complete the following Lean 4 theorem proof.\n\n{example['header']}\n{example['formal_statement']}"
    assistant_msg = example["nl_proof"]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": assistant_msg},
    ]

    # Try chat template, fall back to manual formatting
    try:
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    except Exception:
        text = f"<|system|>\n{SYSTEM_PROMPT}\n<|user|>\n{user_msg}\n<|assistant|>\n{assistant_msg}"

    return text


def main():
    args = parse_args()
    print(f"Config: {vars(args)}")

    # -- Load tokenizer --
    print(f"Loading tokenizer: {args.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # -- Load and format dataset --
    print(f"Loading dataset: {args.dataset_name}")
    ds = load_dataset(args.dataset_name)
    train_ds = ds["validation"]  # train on val split
    eval_ds = ds["test"]         # eval on test split

    def format_fn(example):
        example["text"] = format_example(example, tokenizer)
        return example

    train_ds = train_ds.map(format_fn)
    eval_ds = eval_ds.map(format_fn)

    print(f"Train examples: {len(train_ds)}, Eval examples: {len(eval_ds)}")
    print(f"Sample formatted text (truncated):\n{train_ds[0]['text'][:500]}\n...")

    # -- Load model --
    print(f"Loading model: {args.model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False  # required for gradient checkpointing

    # -- LoRA config --
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "up_proj", "down_proj", "gate_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )

    # -- Training args --
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        bf16=True,
        logging_steps=1,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        seed=args.seed,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        report_to="none",
        remove_unused_columns=False,
    )

    # -- Trainer --
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        peft_config=lora_config,
        processing_class=tokenizer,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        packing=False,
    )

    # -- Eval before training (baseline) --
    print("Evaluating baseline (before training)...")
    baseline = trainer.evaluate()
    print(f"Baseline eval loss: {baseline['eval_loss']:.4f}")

    # -- Train --
    print("Starting LoRA training...")
    trainer.train()

    # -- Final eval --
    print("Final evaluation...")
    final = trainer.evaluate()
    print(f"Final eval loss: {final['eval_loss']:.4f}")
    print(f"Improvement: {baseline['eval_loss'] - final['eval_loss']:.4f}")

    # -- Save --
    trainer.save_model(f"{args.output_dir}/final")
    tokenizer.save_pretrained(f"{args.output_dir}/final")
    print(f"Model saved to {args.output_dir}/final")


if __name__ == "__main__":
    main()
