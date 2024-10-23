from interactor import DoomInteractor

import torch
from torch import nn



class Agent(torch.nn.Module):
    def __init__(self):
        super().__init__()

        # doom action space is Discrete(8) so we want
        # to output a distribution over 8 actions

        # observation shape is (240, 320, 3)
        # output should be a vector of 8 (our means)
        self.model = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=32, kernel_size=8, stride=4),  # (32, 58, 78)
            nn.ReLU(),
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=4, stride=2),  # (64, 28, 38)
            nn.ReLU(),
            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, stride=1),  # (64, 26, 36)
            nn.ReLU(),

            nn.AdaptiveAvgPool2d((1, 1)),  # (64, 1, 1)
            nn.Flatten(),

            nn.Linear(in_features=64, out_features=128),
            nn.ReLU(),
            nn.Linear(in_features=128, out_features=8),  # Final output shape is 8 (the action logits)
        )

        # temperature/std variable
        self.temperature = torch.nn.Parameter(torch.tensor(1.0))

    def get_distribution(self, means: torch.Tensor) -> torch.distributions.Normal:
        dist = torch.distributions.Normal(means, self.temperature)
        return dist

    def forward(self, observations: torch.Tensor):
        # make float and reorder to (batch, channels, height, width) from (batch, height, width, channels)
        observations = observations.float().permute(0, 3, 1, 2)
        means = self.model(observations)
        dist = self.get_distribution(means)
        print(dist)
        print(dist.sample().shape)
        print(dist.sample()[0])


        exit()


if __name__ == "__main__":
    agent = Agent()

    MAX_STEPS = 100
    NUM_ENVS = 16
    
    # if true one of the environments will be displayed in a cv2 window
    WATCH = False
    
    interactor = DoomInteractor(NUM_ENVS, watch=WATCH)

    # Reset all environments
    observations = interactor.env.reset()
    # print("Initial Observations:", observations.shape)

    # Example of stepping through the environments
    for _ in range(100):  # Step for 100 frames or episodes
        actions = agent.forward(observations.float())

        print(actions.shape)
        exit()

        observations, rewards, dones = interactor.step()
        print(observations.shape, rewards.shape)

    # Close all environments
    interactor.env.close()
