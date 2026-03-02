from trainer import Trainer
from model import CNN
import hydra
from omegaconf import OmegaConf, DictConfig
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import torch

# different training methods
from contrastive import ContrastiveLearning
from ebt import EBTTrainer

@hydra.main(version_base=None, config_path="./", config_name="config")
def main(cfg: DictConfig):
    conf = OmegaConf.to_container(cfg, resolve=True)
    conf = OmegaConf.create(conf)
    torch.set_printoptions(sci_mode=False, precision=5)

    # NNIST Dataset
    dataset = datasets.MNIST(
        root='../../4D-Dyn/flow-matching-mnist/data/', 
        train=True, 
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=0.5, std=0.5) # Result in -1 t 1
        ]),
        download=True
    )
    
    trainer = Trainer(
        model=EBTTrainer(CNN(conf), conf),
        config=conf
    )

    dl = DataLoader(
        dataset, 
        batch_size=conf.training.batch_size, 
        shuffle=True, 
        num_workers=conf.memory.num_workers
    )

    # Training phrase
    print("Training...")
    for _ in range(conf.training.num_episodes): # trainer tracks steps internally
        trainer.train(
            dl=dl, 
            unpack=lambda x: {"x": x[0], "condition": x[1]}
        )

if __name__ == "__main__":
    main()

