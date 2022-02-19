import gpytorch
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

gpytorch_available = True
cuda_available = torch.cuda.is_available()

# cf.
# https://github.com/cornellius-gp/gpytorch/blob/master/examples/02_Scalable_Exact_GPs/Simple_GP_Regression_With_LOVE_Fast_Variances_and_Sampling.ipynb

# The Deep RBF kernel (DKL) uses a neural network as an initial feature extractor.
class LargeFeatureExtractor(torch.nn.Sequential):
    def __init__(self, input_dim):
        super(LargeFeatureExtractor, self).__init__()
        self.add_module("linear1", torch.nn.Linear(input_dim, 1000))
        self.add_module("relu1", torch.nn.ReLU())
        self.add_module("linear2", torch.nn.Linear(1000, 500))
        self.add_module("relu2", torch.nn.ReLU())
        self.add_module("linear3", torch.nn.Linear(500, 50))
        self.add_module("relu3", torch.nn.ReLU())
        self.add_module("linear4", torch.nn.Linear(50, 2))


# Our GRP model for training and predictions
class GPRegressionModel(gpytorch.models.ExactGP):
    def __init__(self, x_sub, y_sub, subsample, shape, likelihood):

        self.x_size = shape[1]
        self.y_size = shape[0]
        # map numpy arrays to normalized tensors
        y_sub = torch.tensor(y_sub / self.y_size).float()
        x_sub = torch.tensor(x_sub / self.x_size).float()
        train_x = torch.cat(
            (
                y_sub.contiguous().view(y_sub.numel(), 1),
                x_sub.contiguous().view(x_sub.numel(), 1),
            ),
            dim=1,
        )
        train_y = torch.tensor(subsample / (2**16)).float()

        super(GPRegressionModel, self).__init__(train_x, train_y, likelihood)

        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.RBFKernel(ard_num_dims=2)
            gpytorch.kernels.LinearKernel(num_dimensions=2)
        )
        self.feature_extractor = LargeFeatureExtractor(input_dim=train_x.size(-1))
        self.scale_to_bounds = gpytorch.utils.grid.ScaleToBounds(-1.0, 1.0)
        self.train_x = train_x
        self.train_y = train_y

    def forward(self, x):
        # We're first putting our data through a deep net (feature extractor)
        # We're also scaling the features so that they're nice values
        projected_x = self.feature_extractor(x)
        projected_x = self.scale_to_bounds(projected_x)
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)


def train(model, likelihood, training_iterations=range(100)):
    # Find optimal model hyperparameters
    model.train()
    likelihood.train()

    # Use the adam optimizer
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.01,
    )  # Includes GaussianLikelihood parameters

    train_x, train_y = (model.train_x, model.train_y)
    if torch.cuda.is_available:
        train_x, train_y, likelihood, model = (
            train_x.cuda(),
            train_y.cuda(),
            likelihood.cuda(),
            model.cuda(),
        )
    else:
        print(
            "WARNING: pytorch has no CUDA support, cf. https://pytorch.org/get-started/locally/"
        )

    # "Loss" for GPs - the marginal log likelihood
    mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)

    for i in training_iterations:
        print("training iteration", i)
        optimizer.zero_grad()
        output = model(train_x)
        loss = -mll(output, train_y)
        loss.backward()
        optimizer.step()


def predict(model, likelihood):
    yv, xv = torch.meshgrid(
        [
            torch.linspace(0, 1, model.y_size),
            torch.linspace(0, 1, model.x_size),
        ]
    )
    test_x = torch.stack([yv, xv], -1).squeeze(1).contiguous()
    test_y = torch.zeros(model.y_size, 1).contiguous()

    if torch.cuda.is_available:
        test_x, test_y, likelihood, model = (
            test_x.cuda(),
            test_y.cuda(),
            likelihood.cuda(),
            model.cuda(),
        )
    else:
        print(
            "WARNING: pytorch has no CUDA support, cf. https://pytorch.org/get-started/locally/"
        )

    test_dataset = TensorDataset(test_x, test_y)
    test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)

    print("calculating predictions")

    # Set into eval mode
    model.eval()
    likelihood.eval()

    means = torch.zeros(model.x_size, 1).reshape(1, -1)
    with torch.no_grad(), gpytorch.settings.fast_pred_var(), gpytorch.settings.max_preconditioner_size(
        100
    ):
        for x_batch, y_batch in test_loader:
            print("processing batch", means.shape)
            test_loader.batch_size
            preds = likelihood(model(x_batch))
            means = torch.cat([means, preds.mean.cpu()])
    means = means[1:]
    means = means * (2**16)

    return means.numpy()
