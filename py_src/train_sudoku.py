"""
6x6 Sudoku IRED Training Script

Generates Sudoku puzzles and trains IRED model for puzzle completion.
"""

import os
# Set CUDA device before importing torch to avoid MPS interference
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'  # Use all 3 GPUs

import torch
from torch.utils.data import DataLoader
import hydra
from omegaconf import OmegaConf, DictConfig
import numpy as np

from models.sudoku_ired import SudokuEnergy
from ebm.sudoku_ired import SudokuIREDTrainer
from envs.sudoku import Sudoku6x6, SudokuDataset
from utils.trainer import Trainer


@hydra.main(version_base=None, config_path="./config/", config_name="sudoku")
def main(cfg: DictConfig):
    conf = OmegaConf.to_container(cfg, resolve=True)
    conf = OmegaConf.create(conf)
    torch.set_printoptions(sci_mode=False, precision=5)

    # Set device - check CUDA availability first
    if torch.cuda.is_available():
        device = "cuda"
        print(f"CUDA available - using GPU")
        print(f"GPU Count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        device = "cpu"
        print("CUDA not available, using CPU")
        conf.training.device = device

    print("=" * 60)
    print("6x6 Sudoku IRED Training")
    print("=" * 60)
    print(f"Device: {device}")
    print(f"Training samples: {conf.sudoku.num_train_samples}")
    print(f"Test samples: {conf.sudoku.num_test_samples}")
    print(f"Batch size: {conf.training.batch_size}")
    print(f"Epochs: {conf.training.epochs}")
    print("=" * 60)

    # Create checkpoint directory
    os.makedirs(conf.training.checkpoint_dir, exist_ok=True)

    # Generate datasets
    print("\nGenerating Sudoku datasets...")
    print("This may take a few minutes...")

    train_dataset = SudokuDataset(
        num_samples=conf.sudoku.num_train_samples,
        mask_ratio=conf.sudoku.train_mask_ratio
    )

    test_dataset = SudokuDataset(
        num_samples=conf.sudoku.num_test_samples,
        mask_ratio=conf.sudoku.test_mask_ratio
    )

    print(f"\nGenerated {len(train_dataset)} training samples")
    print(f"Generated {len(test_dataset)} test samples")

    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=conf.training.batch_size,
        shuffle=True,
        num_workers=conf.memory.num_workers,
        pin_memory=True if device == "cuda" else False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=conf.training.batch_size,
        shuffle=False,
        num_workers=conf.memory.num_workers,
        pin_memory=True if device == "cuda" else False
    )

    # Initialize model and trainer
    print("\nInitializing model...")
    model = SudokuIREDTrainer(
        SudokuEnergy(conf),
        conf
    )

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")

    # Create trainer wrapper
    trainer = Trainer(
        model=model,
        config=conf,
        train_dataloader=train_loader,
        val_dataloader=test_loader
    )

    # Training
    print("\nStarting training...")
    print("=" * 60)

    trainer.train(
        unpack=lambda x: {
            "x": x[0],      # complete solution tensor
            "condition": x[2]  # mask pattern
        }
    )

    # Final evaluation
    print("\n" + "=" * 60)
    print("Running final evaluation...")
    print("=" * 60)

    evaluate_sudoku_solving(model, test_dataset, conf)

    trainer.finish()


def evaluate_sudoku_solving(model, test_dataset, conf):
    """
    Evaluate puzzle solving accuracy.

    Tests the model's ability to complete partial Sudoku puzzles.
    """
    device = conf.training.device
    model.eval()
    env = Sudoku6x6()

    # Metrics
    total_correct = 0
    total_cells = 0
    valid_solutions = 0
    total_evaluated = 0

    print("\nEvaluating on test set...")

    with torch.no_grad():
        for i in range(min(50, len(test_dataset))):
            if (i + 1) % 10 == 0:
                print(f"  Evaluated {i + 1}/50 samples")

            partial, solution, mask = test_dataset[i]

            # Move to device
            partial = partial.unsqueeze(0).to(device)
            mask = mask.unsqueeze(0).to(device)

            # Solve puzzle using annealed sampling
            completed = model.sample_annealed(
                partial.shape,
                condition=mask,
                steps_per_landscape=conf.sudoku_ired.inference_steps_per_landscape,
                step_size=conf.sudoku_ired.inference_step_size
            )

            # Convert to grids
            predicted_grid = env.probability_tensor_to_grid(completed[0].cpu())
            solution_grid = env.probability_tensor_to_grid(solution)

            # Count correct filled cells (only for originally empty cells)
            original_mask = mask[0, 0].cpu().numpy()
            empty_cells = original_mask == 0
            correct = ((predicted_grid == solution_grid) & empty_cells).sum()

            total_correct += correct
            total_cells += empty_cells.sum()

            # Validate solution constraints
            if env.validate_solution(predicted_grid, original_mask):
                valid_solutions += 1

            total_evaluated += 1

    # Print results
    print("\n" + "=" * 60)
    print("Evaluation Results")
    print("=" * 60)

    cell_accuracy = total_correct / total_cells if total_cells > 0 else 0
    validity_rate = valid_solutions / total_evaluated if total_evaluated > 0 else 0

    print(f"\nCell-level Accuracy:")
    print(f"  Correct cells: {total_correct}/{total_cells}")
    print(f"  Accuracy: {cell_accuracy:.4f} ({cell_accuracy*100:.2f}%)")

    print(f"\nSolution Validity:")
    print(f"  Valid solutions: {valid_solutions}/{total_evaluated}")
    print(f"  Validity rate: {validity_rate:.4f} ({validity_rate*100:.2f}%)")

    # Show some examples
    print("\n" + "=" * 60)
    print("Example Solutions")
    print("=" * 60)

    num_examples = min(3, total_evaluated)
    for i in range(num_examples):
        partial, solution, mask = test_dataset[i]

        partial = partial.unsqueeze(0).to(device)
        mask = mask.unsqueeze(0).to(device)

        completed = model.sample_annealed(
            partial.shape,
            condition=mask
        )

        predicted_grid = env.probability_tensor_to_grid(completed[0].cpu())
        solution_grid = env.probability_tensor_to_grid(solution)
        partial_grid = env.probability_tensor_to_grid(partial[0].cpu())

        print(f"\nExample {i + 1}:")
        print("Partial puzzle (0 = empty):")
        print(partial_grid)

        print("Predicted solution:")
        print(predicted_grid)

        print("Ground truth solution:")
        print(solution_grid)

        # Check correctness
        correct = ((predicted_grid == solution_grid) & (mask[0, 0].cpu().numpy() == 0)).sum()
        total_empty = (mask[0, 0].cpu().numpy() == 0).sum()
        print(f"Correct cells: {correct}/{total_empty}")

        is_valid = env.validate_solution(predicted_grid, mask[0, 0].cpu().numpy())
        print(f"Valid solution: {is_valid}")


if __name__ == "__main__":
    main()
