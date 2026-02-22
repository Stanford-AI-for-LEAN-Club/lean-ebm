from trainer import Trainer
from model import CNN
import torchvision
import hydra
from omegaconf import OmegaConf, DictConfig
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset, Dataset

@hydra.main(version_base=None, config_path="./", config_name="config")
def main(cfg: DictConfig):
    conf = OmegaConf.to_container(cfg, resolve=True)
    conf = OmegaConf.create(conf)

    # NNIST Dataset
    mnist_mean = (0.1307,)
    mnist_std = (0.3081,)
    dataset = datasets.MNIST(
        root='../../4D-Dyn/flow-matching-mnist/data/', 
        train=True, 
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=mnist_mean, std=mnist_std) # Result is ~N(0, 1)
        ]),
        download=True
    )

    #trainer = trainer(CNN, )
    trainer = Trainer(model=CNN(conf), config=conf)

    # Training phrase
    print("Training...")
    for _ in range(conf.training.num_episodes): # trainer tracks steps internally
        dl = DataLoader(
            dataset, 
            batch_size=conf.training.batch_size, 
            shuffle=True, 
            num_workers=conf.memory.num_workers
        )
        trainer.train(dl=dl)

if __name__ == "__main__":
    main()

