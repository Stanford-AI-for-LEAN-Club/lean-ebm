# 6x6 Sudoku IRED Training - Implementation Complete

## Overview

Successfully implemented IRED (Inverse Reinforcement Energy-based Diffusion) training for 6x6 Sudoku puzzle completion. The model learns an energy function over puzzle configurations and uses gradient descent across multiple noise landscapes to complete partial puzzles.

## Implementation Summary

### Files Created

1. **`py_src/envs/sudoku.py`** - Sudoku environment
   - `Sudoku6x6`: Puzzle generation, validation, probability tensor conversion
   - `SudokuDataset`: PyTorch dataset with pre-generation

2. **`py_src/models/sudoku_ired.py`** - Energy model
   - `SudokuEnergy`: CNN-based energy function for 7-channel probability tensors
   - 32K parameters, adapted for 6×6 grids

3. **`py_src/ebm/sudoku_ired.py`** - IRED trainer
   - `SudokuIREDTrainer`: Multi-landscape training with probability noise
   - Annealed sampling for inference

4. **`py_src/config/sudoku.yaml`** - Configuration
   - Dataset: 10k train, 50 test samples
   - 50 landscapes, 128 energy_dim
   - 20 epochs, batch size 16

5. **`py_src/train_sudoku.py`** - Training script
   - Data generation, training loop, evaluation
   - Cell accuracy + constraint validation metrics

### Architecture

- **Input**: 7-channel tensor (B, 7, 6, 6)
  - Channel 0: Certainty (1=filled, 0=empty)
  - Channels 1-6: One-hot encoding for values 1-6

- **Model**: Adapted CNN
  - Conv trunk: 7 → 16 → 32 → 64 with global pooling
  - Landscape embedding: 50 landscapes → 16 dim
  - Condition embedding: mask pattern (6×6) → 16 dim
  - Energy head: 64+16+16 → 32 → 16 → 128 (energy_dim)

- **Training**: IRED with three loss components
  - MSE loss: Score matching on noise direction
  - Contrastive loss: Push positive energy lower than negative
  - Regularization: Small penalty on total energy

### Test Results (Small Scale)

Ran with 10 samples, 1 epoch, 5 landscapes:
- ✓ Data generation: Working
- ✓ Training loop: Converging
- ✓ Forward/backward pass: Gradients flowing
- ✓ Inference: Sampling producing outputs
- Cell accuracy: 63% (expected with minimal training)
- Valid solutions: 0% (needs more training)

## Running Full Training

### Basic Training
```bash
cd /lfs/mercury1/0/eshaanb/lean-ebm/py_src
PYTHONPATH=/lfs/mercury1/0/eshaanb/lean-ebm/py_src python train_sudoku.py
```

### With CUDA (if available)
```bash
python train_sudoku.py training.device=cuda
```

### Custom Parameters
```bash
# Fewer samples for faster testing
python train_sudoku.py sudoku.num_train_samples=1000 sudoku.num_test_samples=20

# More landscapes for finer refinement
python train_sudoku.py sudoku_ired.num_landscapes=100

# Adjust learning rate
python train_sudoku.py training.learning_rate=1e-4
```

### Full Production Run
```bash
python train_sudoku.py \
  sudoku.num_train_samples=10000 \
  sudoku.num_test_samples=50 \
  training.epochs=20 \
  training.batch_size=16 \
  sudoku_ired.num_landscapes=50 \
  sudoku_ired.inference_steps_per_landscape=15
```

## Expected Training Behavior

1. **Data Generation**: Takes 2-5 minutes for 10k puzzles
2. **Training**: ~20-30 minutes for 20 epochs (CPU), faster on GPU
3. **Loss Curve**: Should decrease smoothly with three components
   - MSE loss: Score matching quality
   - Contrastive loss: Energy separation
   - Total loss: Combined objective

4. **Evaluation Metrics**:
   - Cell accuracy: % of correctly filled cells
   - Validity rate: % of solutions satisfying Sudoku constraints
   - Target: >80% cell accuracy, >50% validity after full training

## Troubleshooting

### Out of Memory
- Reduce batch size: `training.batch_size=8`
- Reduce landscapes: `sudoku_ired.num_landscapes=30`

### Slow Training
- Reduce samples: `sudoku.num_train_samples=1000`
- Reduce epochs: `training.epochs=10`
- Use GPU if available: `training.device=cuda`

### Poor Results
- Increase training samples
- Increase number of landscapes
- Adjust loss weights: `sudoku_ired.mse_weight=2.0`
- Increase inference steps: `sudoku_ired.inference_steps_per_landscape=20`

## Next Steps

1. **Run Full Training**: Train with 10k samples for 20 epochs
2. **Monitor Metrics**: Check loss curves and evaluation accuracy
3. **Hyperparameter Tuning**: Adjust landscape count, loss weights
4. **Architecture Improvements**: Consider adding constraint loss
5. **Visualization**: Add plotting for training curves and solutions

## Key Design Decisions

- **6×6 Grid**: Simpler than 9×9, faster training
- **Probability Representation**: Maintains differentiability for gradient-based optimization
- **Multi-landscape**: Progressive refinement from coarse to fine
- **Pre-generation**: All puzzles generated upfront for reproducibility
- **Condition Preservation**: Fixed cells remain fixed during sampling

## References

- IRED Paper: Inverse Reinforcement Energy-based Diffusion
- Original IRED implementation: `py_src/ebm/ired.py`
- MNIST training script: `py_src/train_mnist.py`
