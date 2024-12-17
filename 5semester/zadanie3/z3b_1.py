import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import datetime

# value of loss function to stop the training
EARLY_STOPPING_TRESHOLD = 0.01

# definition of the neural network model
class NN_Model(nn.Module):
    # input_size - first layer for all the features
    def __init__(self, input_size):
        super(NN_Model, self).__init__()
        self.inputLayer = nn.Linear(input_size, 128)
        self.hiddenLayer1 = nn.Linear(128, 128)
        # extra hidden layer used when testing
        # self.hiddenLayer2 = nn.Linear(128, 64)
        # we are predicting only 1 feature so output size is 1
        self.outputLayer = nn.Linear(128, 1)
        self.active_func = nn.ReLU()

    def forward(self, x):
        x = self.active_func(self.inputLayer(x))
        x = self.active_func(self.hiddenLayer1(x))
        # x = self.active_func(self.hiddenLayer2(x))
        x = self.outputLayer(x)
        return x

# train the model with batching
def train_model(model, optimizer, train_loader, test_loader, loss_func, num_epochs=300):
    # lists for storing the losses through the epochs
    train_losses, test_losses = [], []
    early_stopping = False
    # how many epochs to wait after the early stopping treshold is reached
    patience = 10
    for epoch in range(num_epochs):
        
        if early_stopping:
            if patience == 0:
                break
            patience -= 1
        
        if epoch % 10 == 0:
            print("Epoch: ", epoch)
            
        model.train()
        batch_train_losses = []
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            predictions = model(batch_X).squeeze()
            loss = loss_func(predictions, batch_y)
            loss.backward()
            optimizer.step()
            batch_train_losses.append(loss.item())
        
        # average loss for one epoch
        train_loss = sum(batch_train_losses) / len(batch_train_losses)
        
        if train_loss < EARLY_STOPPING_TRESHOLD:
            early_stopping = True
        
        # evaluation / prediction on testing data
        model.eval()
        with torch.no_grad():
            batch_test_losses = []
            for batch_X, batch_y in test_loader:
                predictions = model(batch_X).squeeze()
                loss = loss_func(predictions, batch_y)
                batch_test_losses.append(loss.item())
            test_loss = sum(batch_test_losses) / len(batch_test_losses)

        train_losses.append(train_loss)
        test_losses.append(test_loss)

    return train_losses, test_losses


def main():
    # loading the dataset using sklearn
    data = fetch_california_housing()
    X, y = data.data, data.target

    # split the data into training and testing wih 80:20 ratio
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # normalization of the data
    # MinMaxScaler range by default <0, 1>
    scaler_X = MinMaxScaler()
    X_train = scaler_X.fit_transform(X_train)
    X_test = scaler_X.transform(X_test)

    scaler_y = MinMaxScaler()
    y_train = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
    y_test = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

    # for pytorch nn models, need to convert the data into tensors
    X_train, y_train = torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32)
    X_test, y_test = torch.tensor(X_test, dtype=torch.float32), torch.tensor(y_test, dtype=torch.float32)

    # create DataLoader for batching
    batch_size = 128
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # model creation
    model = NN_Model(X_train.shape[1])

    # loss function
    # MSE - Mean Squared Error
    loss_func = nn.MSELoss()

    # config for optimizers
    optimizers = {
        "SGD": optim.SGD(model.parameters(), lr=0.01),
        "SGD with Momentum": optim.SGD(model.parameters(), lr=0.01, momentum=0.95),
        "Adam": optim.Adam(model.parameters(), lr=0.01)
    }

    # train model for each optimizer
    results = {}
    for name, optimizer in optimizers.items():
        print(f"Training with {name} optimizer: ")
        train_losses, test_losses = train_model(model, optimizer, train_loader, test_loader, loss_func)
        results[name] = (train_losses, test_losses)

    # plot all of the results (train and test losses for each optimizer)
    plt.figure(figsize=(28.8, 16.2), dpi=100)
    for name, (train_losses, test_losses) in results.items():
        plt.plot(train_losses, label=f'{name} Train Loss')
        plt.plot(test_losses, label=f'{name} Test Loss')

    # results in console
    for name, (train_losses, test_losses) in results.items():
        print(f"{name} min train loss: {min(train_losses)}")
        print(f"{name} min test loss: {min(test_losses)}")

    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Loss function for optimizers')
    
    # save the plot with date time
    now = datetime.datetime.now()
    plt.savefig(f"./plots/z3b_1__{now.strftime('%Y-%m-%d_%H-%M-%S')}.png")

if __name__ == "__main__":
    main()
    