from utils.trainer import Trainer
from models.ired import IREDEnergy
from models.cnn import CNN
import hydra
from omegaconf import OmegaConf, DictConfig
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import torch

# different training methods
from ebm.contrastive import ContrastiveLearning
from ebm.ebt import EBTTrainer
from ebm.ired import IREDTrainer

@hydra.main(version_base=None, config_path="./config/", config_name="conf")
def main(cfg: DictConfig):
    conf = OmegaConf.to_container(cfg, resolve=True)
    conf = OmegaConf.create(conf)
    torch.set_printoptions(sci_mode=False, precision=5)

    # NNIST Dataset
    dataset = datasets.MNIST(
        root='../data/', 
        train=True, 
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=0.5, std=0.5) # Result in -1 t 1
        ]),
        download=True
    )
    
    # filter the dataset
    def get_digit_loader(dataset, digit):
        indices = [i for i, label in enumerate(dataset.targets) if label == digit]
        return Subset(dataset, indices)
    #dataset = get_digit_loader(dataset, 8)

    trainer = Trainer(
        model=EBTTrainer(CNN(conf), conf),
        config=conf,
    )

    dl = DataLoader(
        dataset, 
        batch_size=conf.training.batch_size, 
        shuffle=True, 
        num_workers=conf.memory.num_workers
    )

    # Training phrase
    print("Training...")
    trainer.train(
        dl=dl,
        # convert from "batch" in "for batch in "
        unpack=lambda x: {"x": x[0], "condition": x[1]} 
    )

if __name__ == "__main__":
    main()


