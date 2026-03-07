# Most of this code generated via ChatGPT and then fine-tuned
import os
import torch
from omegaconf import DictConfig
from typing import Union
from accelerate import Accelerator
from torch.optim import Adam, SGD, AdamW

class Trainer:
    def __init__(self, model, config: DictConfig, train_dataloader=None, val_dataloader=None):
        self.config = config

        # 2. Initialize Accelerator for multi-GPU / mixed precision support
        self.accelerator = Accelerator(
            gradient_accumulation_steps=config.training.gradient_accumulation_steps,
            log_with="wandb"
        )

        # 3. Setup WandB via Accelerator
        wandb_kargs = { "entity": config.wandb.entity }
        if len(n := config.wandb.get("name", "")) > 0:
            wandb_kargs["name"] = n
        if len(n := config.wandb.get("notes", "")) > 0:
            wandb_kargs["notes"] = n

        # ============== Change this ==============
        self.accelerator.init_trackers(
            project_name=config.wandb.project,
            config=dict(config),
            init_kwargs={"wandb": wandb_kargs}
        )

        # 4. Optimizer
        # You can experiment with this with norm_space and norm_time
        self.optimizer = AdamW(
            model.parameters(),
            lr=config.training.learning_rate,
            betas=(0.9, 0.999),
            weight_decay=config.training.weight_decay
        )
        """
        self.optimizer = SGD(
            model.parameters(),
            lr=config.training.learning_rate
        )
        """

        # 5. Prepare everything with Accelerator
        # This handles moving models to GPU and wrapping them for Distributed Data Parallel
        self.model, self.optimizer = self.accelerator.prepare(model, self.optimizer)

        if train_dataloader is not None:
            self.train_dataloader = self.accelerator.prepare(train_dataloader)
        else:
            self.train_dataloader = None

        if val_dataloader is not None:
            self.val_dataloader = self.accelerator.prepare(val_dataloader)
        else:
            self.val_dataloader = None

        self.reset()

    def reset (self):
        self.total_steps = 0

    def train(self, dl=None, unpack=None): # override the dl
        assert self.train_dataloader is not None or dl is not None
        dl = self.accelerator.prepare(dl) if dl is not None else self.train_dataloader

        self.model.train()

        for epoch in range(self.config.training.epochs):
            for batch in dl:
                # Accelerator handles accumulation context automatically
                with self.accelerator.accumulate(self.model):

                    # Model is expected to return (loss, predictions)
                    loss, logs = self.model(**unpack(batch))
                    self.accelerator.backward(loss)

                    # 5. Gradient Clipping
                    if self.accelerator.sync_gradients:
                        self.accelerator.clip_grad_norm_(
                            self.model.parameters(),
                            self.config.training.max_grad_norm
                        )

                    # Step through optimizer
                    self.optimizer.step()
                    self.optimizer.zero_grad()

                # Logging
                if self.accelerator.sync_gradients:
                    self.total_steps += 1

                    self.accelerator.log(logs)

                    # Print every N steps to avoid flooding the console
                    if (self.total_steps+1) % self.config.training.get("print_every", 10) == 0:
                        st = f"Step {self.total_steps+1} | Train Loss: {loss:.4f}"
                        for key, value in logs.items():
                            if isinstance(value, list) and isinstance(value[0], float): 
                                st += f" | {key}: [" 
                                for k in value:
                                    st += f"{k:.3f}, "
                                st = st[:-2] + "]"
                            else:
                                st += f" | {key}: {value:.4f}" if isinstance(value, float) else f" | {key}: {value}"
                        self.accelerator.print(st)

                    # Save every N steps to save checkpoint
                    if (self.total_steps+1) % self.config.training.get("save_steps", 100) == 0:
                        self.save_checkpoint(epoch)
                        self.evaluate(self.total_steps)

    def log (self, dict_log):
        self.accelerator.log(dict_log)

    @torch.no_grad()
    def evaluate(self, step):
        if self.val_dataloader is None:
            return

        self.model.eval()
        losses = []
        for batch in self.val_dataloader:
            loss, _ = self.model(batch)
            losses.append(self.accelerator.gather_for_metrics(loss))

        avg_loss = torch.mean(torch.stack(losses)).item()
        self.accelerator.log({"val_loss": avg_loss}, step=step)
        self.accelerator.print(f"Steps {step} Val Loss: {avg_loss:.4f}")
        self.model.train()

    def save_checkpoint(self, epoch):
        # Ensure only the main process saves the file
        self.accelerator.wait_for_everyone()
        if self.accelerator.is_main_process:
            path = os.path.join(self.config.training.checkpoint_dir, self.config.model.model_name)
            unwrapped_model = self.accelerator.unwrap_model(self.model)
            self.accelerator.save(unwrapped_model.state_dict(), path)
            self.accelerator.print(f"Saved checkpoint: {path}")

    def finish(self):
        self.accelerator.end_training()