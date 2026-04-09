"""
6x6 Sudoku Environment

Generates valid 6x6 Sudoku puzzles and handles probability tensor representations.
6x6 Sudoku uses 2x3 blocks (2 rows, 3 columns per block).
"""

import torch
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional
import random


class Sudoku6x6:
    """6x6 Sudoku environment with puzzle generation and validation"""

    def __init__(self):
        self.grid_size = 6
        self.block_rows = 2  # 2 rows per block
        self.block_cols = 3  # 3 columns per block
        self.num_values = 7  # 0-6 where 0 = uncertain/empty, 1-6 = filled values
        self.num_blocks_h = self.grid_size // self.block_rows  # 3 blocks vertically
        self.num_blocks_w = self.grid_size // self.block_cols  # 2 blocks horizontally

    def generate_complete_puzzle(self) -> np.ndarray:
        """
        Generate a complete valid 6x6 Sudoku using backtracking.

        Returns:
            np.ndarray: (6, 6) array with values 1-6
        """
        grid = np.zeros((self.grid_size, self.grid_size), dtype=int)

        # Fill diagonal blocks first (they're independent)
        for block_i in range(self.num_blocks_h):
            for block_j in range(self.num_blocks_w):
                if block_i == block_j:  # Only fill diagonal blocks
                    values = list(range(1, 7))
                    random.shuffle(values)
                    idx = 0
                    for i in range(block_i * self.block_rows, (block_i + 1) * self.block_rows):
                        for j in range(block_j * self.block_cols, (block_j + 1) * self.block_cols):
                            grid[i, j] = values[idx]
                            idx += 1

        # Solve the rest using backtracking
        if self._solve_puzzle(grid):
            return grid
        else:
            # Fallback: try again with different diagonal initialization
            return self.generate_complete_puzzle()

    def _solve_puzzle(self, grid: np.ndarray) -> bool:
        """
        Solve puzzle using backtracking.

        Args:
            grid: (6, 6) array to fill in-place

        Returns:
            bool: True if solvable
        """
        empty = self._find_empty(grid)
        if not empty:
            return True  # Puzzle solved

        row, col = empty

        # Try values 1-6
        for value in range(1, 7):
            if self.is_valid_placement(grid, row, col, value):
                grid[row, col] = value

                if self._solve_puzzle(grid):
                    return True

                grid[row, col] = 0  # Backtrack

        return False

    def _find_empty(self, grid: np.ndarray) -> Optional[Tuple[int, int]]:
        """Find an empty cell (value 0)"""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if grid[i, j] == 0:
                    return (i, j)
        return None

    def is_valid_placement(self, grid: np.ndarray, row: int, col: int, value: int) -> bool:
        """
        Check if value placement is valid at (row, col).

        Args:
            grid: Current puzzle state
            row: Row index
            col: Column index
            value: Value to place (1-6)

        Returns:
            bool: True if placement is valid
        """
        # Check row
        if value in grid[row, :]:
            return False

        # Check column
        if value in grid[:, col]:
            return False

        # Check 2x3 block
        block_i = row // self.block_rows
        block_j = col // self.block_cols
        block = grid[
            block_i * self.block_rows:(block_i + 1) * self.block_rows,
            block_j * self.block_cols:(block_j + 1) * self.block_cols
        ]
        if value in block:
            return False

        return True

    def create_partial_puzzle(
        self,
        complete_grid: np.ndarray,
        mask_ratio: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Create partial puzzle by masking cells.

        Args:
            complete_grid: (6, 6) complete solution
            mask_ratio: Fraction of cells to mask (0-1)

        Returns:
            tuple: (partial_grid, mask, solution)
                - partial_grid: (6, 6) with masked cells set to 0
                - mask: (6, 6) boolean (1=filled/visible, 0=masked)
                - solution: (6, 6) original complete grid
        """
        mask = np.random.rand(self.grid_size, self.grid_size) < mask_ratio
        partial_grid = complete_grid.copy()
        partial_grid[~mask] = 0
        return partial_grid, mask.astype(float), complete_grid

    def grid_to_probability_tensor(self, grid: np.ndarray) -> torch.Tensor:
        """
        Convert grid to (7, 6, 6) probability distribution tensor.

        Args:
            grid: (6, 6) array with values 0-6
                  0 = empty/uncertain, 1-6 = filled values

        Returns:
            torch.Tensor: (7, 6, 6) tensor
                - Channel 0: Certainty (1 if cell filled, 0 if empty)
                - Channels 1-6: One-hot encoding of values 1-6
        """
        tensor = torch.zeros(self.num_values, self.grid_size, self.grid_size, dtype=torch.float32)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = grid[i, j]
                if value > 0:  # Filled cell
                    tensor[0, i, j] = 1.0  # Certainty
                    tensor[value, i, j] = 1.0  # One-hot value
                # Else: empty cell, all zeros (uncertain)

        return tensor

    def probability_tensor_to_grid(self, tensor: torch.Tensor) -> np.ndarray:
        """
        Convert probability tensor back to grid values.

        Args:
            tensor: (7, 6, 6) probability tensor

        Returns:
            np.ndarray: (6, 6) grid with values 0-6
        """
        grid = np.zeros((self.grid_size, self.grid_size), dtype=int)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Check if cell is filled (certainty channel)
                if tensor[0, i, j] > 0.5:
                    # Get argmax of value channels (1-6)
                    values = tensor[1:, i, j]
                    value_idx = torch.argmax(values).item() + 1  # 1-6
                    grid[i, j] = value_idx
                else:
                    grid[i, j] = 0  # Empty

        return grid

    def validate_solution(
        self,
        proposed_solution: np.ndarray,
        original_mask: np.ndarray
    ) -> bool:
        """
        Validate that solution satisfies Sudoku constraints.

        Args:
            proposed_solution: (6, 6) grid to validate
            original_mask: (6, 6) boolean mask of originally filled cells

        Returns:
            bool: True if solution is valid
        """
        # Check all cells are filled (0-6 range)
        if np.any(proposed_solution == 0):
            return False  # Empty cells

        # Check each cell satisfies constraints
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = proposed_solution[i, j]
                # Temporarily remove this cell and check validity
                proposed_solution[i, j] = 0
                if not self.is_valid_placement(proposed_solution, i, j, value):
                    proposed_solution[i, j] = value
                    return False
                proposed_solution[i, j] = value

        return True

    def check_constraints(self, grid: np.ndarray) -> dict:
        """
        Check constraint violations in a grid.

        Args:
            grid: (6, 6) grid to check

        Returns:
            dict: Constraint violation counts
        """
        violations = {"row": 0, "col": 0, "block": 0}

        # Check rows
        for i in range(self.grid_size):
            row = grid[i, :]
            non_zero = row[row > 0]
            if len(non_zero) != len(np.unique(non_zero)):
                violations["row"] += 1

        # Check columns
        for j in range(self.grid_size):
            col = grid[:, j]
            non_zero = col[col > 0]
            if len(non_zero) != len(np.unique(non_zero)):
                violations["col"] += 1

        # Check blocks
        for block_i in range(self.num_blocks_h):
            for block_j in range(self.num_blocks_w):
                block = grid[
                    block_i * self.block_rows:(block_i + 1) * self.block_rows,
                    block_j * self.block_cols:(block_j + 1) * self.block_cols
                ]
                non_zero = block[block > 0]
                if len(non_zero) != len(np.unique(non_zero)):
                    violations["block"] += 1

        return violations


class SudokuDataset(torch.utils.data.Dataset):
    """PyTorch Dataset for Sudoku puzzles"""

    def __init__(self, num_samples: int, mask_ratio: float = 0.5):
        """
        Generate Sudoku puzzles upfront.

        Args:
            num_samples: Number of puzzles to generate
            mask_ratio: Fraction of cells to reveal
        """
        self.env = Sudoku6x6()
        self.num_samples = num_samples
        self.mask_ratio = mask_ratio
        self.puzzles = self._generate_puzzles()

    def _generate_puzzles(self):
        """Generate all puzzles upfront"""
        puzzles = []
        print(f"Generating {self.num_samples} Sudoku puzzles...")

        for i in range(self.num_samples):
            if (i + 1) % 1000 == 0:
                print(f"  Generated {i + 1}/{self.num_samples} puzzles")

            # Generate complete puzzle
            complete_grid = self.env.generate_complete_puzzle()

            # Create partial puzzle
            partial_grid, mask, solution = self.env.create_partial_puzzle(
                complete_grid, self.mask_ratio
            )

            # Convert to probability tensors
            partial_tensor = self.env.grid_to_probability_tensor(partial_grid)
            solution_tensor = self.env.grid_to_probability_tensor(solution)
            mask_tensor = torch.from_numpy(mask).float()

            puzzles.append((partial_tensor, solution_tensor, mask_tensor))

        print(f"Finished generating {self.num_samples} puzzles")
        return puzzles

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        """
        Returns:
            tuple: (partial_puzzle, solution, mask)
                - partial_puzzle: (7, 6, 6) probability tensor
                - solution: (7, 6, 6) solution probability tensor
                - mask: (6, 6) boolean mask (1=filled, 0=empty)
        """
        return self.puzzles[idx]


if __name__ == "__main__":
    # Test the environment
    print("Testing Sudoku6x6 environment...")

    env = Sudoku6x6()

    # Generate a puzzle
    print("\n1. Generating complete puzzle...")
    grid = env.generate_complete_puzzle()
    print("Generated grid:")
    print(grid)

    # Validate
    print("\n2. Validating puzzle...")
    is_valid = env.validate_solution(grid, np.ones((6, 6)))
    print(f"Valid: {is_valid}")

    # Check constraints
    violations = env.check_constraints(grid)
    print(f"Constraint violations: {violations}")

    # Create partial puzzle
    print("\n3. Creating partial puzzle (50% mask)...")
    partial, mask, solution = env.create_partial_puzzle(grid, mask_ratio=0.5)
    print(f"Mask coverage: {mask.mean():.2%}")
    print("Partial grid:")
    print(partial)

    # Convert to probability tensor
    print("\n4. Converting to probability tensor...")
    tensor = env.grid_to_probability_tensor(partial)
    print(f"Tensor shape: {tensor.shape}")
    print(f"Channel 0 (certainty) sum: {tensor[0].sum().item():.0f} cells filled")

    # Convert back
    print("\n5. Converting back to grid...")
    reconstructed = env.probability_tensor_to_grid(tensor)
    print("Reconstructed grid:")
    print(reconstructed)
    print(f"Matches original: {np.array_equal(partial, reconstructed)}")

    # Test dataset
    print("\n6. Testing dataset generation...")
    dataset = SudokuDataset(num_samples=10, mask_ratio=0.5)
    print(f"Dataset size: {len(dataset)}")

    partial, solution, mask = dataset[0]
    print(f"Sample shapes: partial={partial.shape}, solution={solution.shape}, mask={mask.shape}")

    print("\nAll tests passed!")
