# Uses CIFAR-10

# Torch stuff
from utils.trainer import Trainer
import hydra
from omegaconf import OmegaConf, DictConfig
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch

# Trainer
from diffusion.diff import DiffusionTrainer

# Models
from models.ired import *
from models.cnn import CNN
from models.unet import UNet

@hydra.main(version_base=None, config_path="./config/", config_name="diffusion")
def main(cfg: DictConfig):
    conf = OmegaConf.to_container(cfg, resolve=True)
    conf = OmegaConf.create(conf)
    torch.set_printoptions(sci_mode=False, precision=5)

    # CIFAR-10 Dataset
    # Note: CIFAR-10 has 3 channels (RGB), so we normalize each channel.
    dataset = datasets.CIFAR10(
        root='../data/', 
        train=True, 
        transform=transforms.Compose([
            transforms.ToTensor(),
            # Normalizing all 3 channels to result in -1 to 1 range
            transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)) 
        ]),
        download=True
    )

    # The Trainer and Model setup remains the same, 
    # but ensure your 'conf' reflects the 3-channel input for CIFAR-10.
    trainer = Trainer(
        model=DiffusionTrainer(UNet(conf), conf),
        config=conf,
    )

    dl = DataLoader(
        dataset, 
        batch_size=conf.training.batch_size, 
        shuffle=True, 
        num_workers=conf.memory.num_workers
    )

    # Training phase
    print("Training on CIFAR-10...")
    trainer.train(
        dl=dl,
        unpack=lambda x: {"x": x[0], "condition": x[1]} 
    )

if __name__ == "__main__":
    main()
