import gpytorch
import numpy as np
import torch
from gpytorch.likelihoods import GaussianLikelihood
from skimage import img_as_uint
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
    def __init__(self, train_x, train_y, likelihood):
        super(GPRegressionModel, self).__init__(train_x, train_y, likelihood)
        
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.RBFKernel(ard_num_dims=2)
            + gpytorch.kernels.LinearKernel()
        )
        self.feature_extractor = LargeFeatureExtractor(input_dim=train_x.size(-1))
        self.scale_to_bounds = gpytorch.utils.grid.ScaleToBounds(-1.0, 1.0)

    def forward(self, x):
        # We're first putting our data through a deep net (feature extractor)
        # We're also scaling the features so that they're nice values
        projected_x = self.feature_extractor(x)
        projected_x = self.scale_to_bounds(projected_x)
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)


class GPRegression:
    def __init__(self, x_sub, y_sub, subsample, shape):
        self.x_size = shape[1]
        self.y_size = shape[0]
        # map numpy arrays to normalized tensors
        y_sub = torch.tensor(y_sub / self.y_size).float()
        x_sub = torch.tensor(x_sub / self.x_size).float()
        self.train_x = torch.cat(
            (
                y_sub.contiguous().view(y_sub.numel(), 1),
                x_sub.contiguous().view(x_sub.numel(), 1),
            ),
            dim=1,
        )
        self.train_y = torch.tensor(subsample).float()

        self.likelihood = GaussianLikelihood()
        self.model = GPRegressionModel(
            self.train_x, self.train_y, likelihood=self.likelihood
        )

    def train(self, training_iterations=range(1000)):
        # Find optimal model hyperparameters
        self.model.train()
        self.likelihood.train()

        # Use the SGD optimizer
        optimizer = torch.optim.SGD(
            self.model.parameters(),
            lr=0.01,
            momentum=0.9
        )  # Includes GaussianLikelihood parameters

        if torch.cuda.is_available:
            self.train_x, self.train_y, self.likelihood, self.model = (
                self.train_x.cuda(),
                self.train_y.cuda(),
                self.likelihood.cuda(),
                self.model.cuda(),
            )
        else:
            print(
                "WARNING: pytorch has no CUDA support, cf. https://pytorch.org/get-started/locally/"
            )

        # "Loss" for GPs - the marginal log likelihood
        mll = gpytorch.mlls.ExactMarginalLogLikelihood(self.likelihood, self.model)

        for i in training_iterations:
            print("training iteration", i)
            optimizer.zero_grad()
            output = self.model(self.train_x)
            loss = -mll(output, self.train_y)
            loss.backward()
            optimizer.step()

    def predict(self):
        yv, xv = torch.meshgrid(
            [
                torch.linspace(0, 1, self.y_size),
                torch.linspace(0, 1, self.x_size),
            ]
        )
        test_x = torch.stack([yv, xv], -1).squeeze(1).contiguous()
        test_y = torch.zeros(self.y_size, 1).contiguous()

        if torch.cuda.is_available:
            test_x, test_y = (test_x.cuda(), test_y.cuda())
        else:
            print(
                "WARNING: pytorch has no CUDA support, cf. https://pytorch.org/get-started/locally/"
            )

        test_dataset = TensorDataset(test_x, test_y)
        test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)

        print("calculating predictions")

        # Set into eval mode
        self.model.eval()
        self.likelihood.eval()

        means = torch.zeros(self.x_size, 1).reshape(1, -1)
        with torch.no_grad(), gpytorch.settings.fast_pred_var(), gpytorch.settings.max_preconditioner_size(
            100
        ):
            for x_batch, y_batch in test_loader:
                print("processing batch", means.shape)
                test_loader.batch_size
                preds = self.likelihood(self.model(x_batch))
                means = torch.cat([means, preds.mean.cpu()])
        means = means[1:]
        result = means.numpy()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return result

    def run(self):
        self.train()
        return self.predict()
