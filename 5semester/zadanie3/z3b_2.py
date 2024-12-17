import numpy as np
import matplotlib.pyplot as plt
import datetime

# definitions of the activation functions and their derivatives
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return sigmoid(x) * (1 - sigmoid(x))


def mse_loss(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

def mse_loss_derivative(y_true, y_pred):
    return -2 * (y_true - y_pred) / y_true.size


def tanh(x):
    return np.tanh(x)

def tanh_derivative(x):
    return 1 - np.tanh(x) ** 2


def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return np.where(x > 0, 1, 0)


# neural network model
# template for the neural network MLP model was sourced from: (documentation - MLP from scratch)
class NN_Model:
    def __init__(self, input_size, hidden_size, output_size, number_of_layers=1, learning_rate=0.1, func="tanh", momentum=0.0):
        self.number_of_layers = number_of_layers
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.func = func
        
        if self.number_of_layers == 1:
            self.weights1 = np.random.randn(input_size, hidden_size)
            self.bias1 = np.zeros((1, hidden_size))
            self.weights2 = np.random.randn(hidden_size, output_size)
            self.bias2 = np.zeros((1, output_size))
            
            # momentum (v_ -> velocity)
            self.v_weights1 = np.zeros_like(self.weights1)
            self.v_bias1 = np.zeros_like(self.bias1)
            self.v_weights2 = np.zeros_like(self.weights2)
            self.v_bias2 = np.zeros_like(self.bias2)
        # elif self.number_of_layers == 2:
        else:
            self.weights1 = np.random.randn(input_size, hidden_size)
            self.bias1 = np.zeros((1, hidden_size))
            self.weights2 = np.random.randn(hidden_size, hidden_size)
            self.bias2 = np.zeros((1, hidden_size))
            self.weights3 = np.random.randn(hidden_size, output_size)
            self.bias3 = np.zeros((1, output_size))
            
            # momentum (v_ -> velocity)
            self.v_weights1 = np.zeros_like(self.weights1)
            self.v_bias1 = np.zeros_like(self.bias1)
            self.v_weights2 = np.zeros_like(self.weights2)
            self.v_bias2 = np.zeros_like(self.bias2)
            self.v_weights3 = np.zeros_like(self.weights3)
            self.v_bias3 = np.zeros_like(self.bias3)

    def forward(self, X):
        self.input = X
        
        if self.func == "sigmoid":
            activation_function = sigmoid
        elif self.func == "tanh":
            activation_function = tanh
        elif self.func == "relu":
            activation_function = relu

        if self.number_of_layers == 1:
            self.hidden = activation_function(np.dot(X, self.weights1) + self.bias1)
            self.output = activation_function(np.dot(self.hidden, self.weights2) + self.bias2)
        # elif self.number_of_layers == 2:
        else:
            self.hidden1 = activation_function(np.dot(X, self.weights1) + self.bias1)
            self.hidden2 = activation_function(np.dot(self.hidden1, self.weights2) + self.bias2)
            self.output = activation_function(np.dot(self.hidden2, self.weights3) + self.bias3)

        return self.output

    def backward(self, X, y_true, y_pred):
        d_loss = mse_loss_derivative(y_true, y_pred)

        if self.func == "sigmoid":
            activation_derivative = sigmoid_derivative
        elif self.func == "tanh":
            activation_derivative = tanh_derivative
        elif self.func == "relu":
            activation_derivative = relu_derivative

        if self.number_of_layers == 1:
            d_output = d_loss * activation_derivative(y_pred)
            d_hidden = np.dot(d_output, self.weights2.T) * activation_derivative(self.hidden)

            d_weights2 = np.dot(self.hidden.T, d_output)
            d_bias2 = np.sum(d_output, axis=0, keepdims=True)
            d_weights1 = np.dot(X.T, d_hidden)
            d_bias1 = np.sum(d_hidden, axis=0, keepdims=True)

            # update weights with momentum
            self.v_weights2 = self.momentum * self.v_weights2 + self.learning_rate * d_weights2
            self.v_bias2 = self.momentum * self.v_bias2 + self.learning_rate * d_bias2
            self.weights2 -= self.v_weights2
            self.bias2 -= self.v_bias2

            self.v_weights1 = self.momentum * self.v_weights1 + self.learning_rate * d_weights1
            self.v_bias1 = self.momentum * self.v_bias1 + self.learning_rate * d_bias1
            self.weights1 -= self.v_weights1
            self.bias1 -= self.v_bias1
        # elif self.number_of_layers == 2:
        else:
            d_output = d_loss * activation_derivative(y_pred)
            d_hidden2 = np.dot(d_output, self.weights3.T) * activation_derivative(self.hidden2)
            d_hidden1 = np.dot(d_hidden2, self.weights2.T) * activation_derivative(self.hidden1)

            d_weights3 = np.dot(self.hidden2.T, d_output)
            d_bias3 = np.sum(d_output, axis=0, keepdims=True)
            d_weights2 = np.dot(self.hidden1.T, d_hidden2)
            d_bias2 = np.sum(d_hidden2, axis=0, keepdims=True)
            d_weights1 = np.dot(X.T, d_hidden1)
            d_bias1 = np.sum(d_hidden1, axis=0, keepdims=True)

            # update weights with momentum
            self.v_weights3 = self.momentum * self.v_weights3 + self.learning_rate * d_weights3
            self.v_bias3 = self.momentum * self.v_bias3 + self.learning_rate * d_bias3
            self.weights3 -= self.v_weights3
            self.bias3 -= self.v_bias3

            self.v_weights2 = self.momentum * self.v_weights2 + self.learning_rate * d_weights2
            self.v_bias2 = self.momentum * self.v_bias2 + self.learning_rate * d_bias2
            self.weights2 -= self.v_weights2
            self.bias2 -= self.v_bias2

            self.v_weights1 = self.momentum * self.v_weights1 + self.learning_rate * d_weights1
            self.v_bias1 = self.momentum * self.v_bias1 + self.learning_rate * d_bias1
            self.weights1 -= self.v_weights1
            self.bias1 -= self.v_bias1

    def train(self, X, y, epochs=500):
        losses = []
        
        print("Losses and predictions through training: ")
        
        for epoch in range(epochs):
            y_pred = self.forward(X)
            loss = mse_loss(y, y_pred)
            losses.append(loss)
            self.backward(X, y, y_pred)
            
            # print every 50 epochs to see the progress
            if epoch % 50 == 0:
                print(f"Epoch {epoch}, Loss: {loss}")
                # show the real and predicted values
                print("Real values: ", y.ravel())
                print("Predicted values rounded: ", np.round(y_pred.ravel()))
                print("Predicted values: ", y_pred.ravel())
                
        return losses

# datasets as tuple of X and y values
datasets = {
    "XOR": (np.array([[0, 0], [0, 1], [1, 0], [1, 1]]), np.array([[0], [1], [1], [0]])),
    "AND": (np.array([[0, 0], [0, 1], [1, 0], [1, 1]]), np.array([[0], [0], [0], [1]])),
    "OR": (np.array([[0, 0], [0, 1], [1, 0], [1, 1]]), np.array([[0], [1], [1], [1]])),
}


def main():
    
    while True:
        print("Select number of layers (enter corresponding number, default 1): ")
        print("0 - EXIT")
        print("1 - 1 Hidden Layer")
        print("2 - 2 Hidden Layer")
        
        number_of_layers = int(input("> "))
        
        if number_of_layers == 0:
            exit()
        
        if number_of_layers == 1 or number_of_layers == 2:
            break
        else:
            print("Invalid input")
        
    while True:
        print("Select activation function (enter corresponding number, default 2): ")
        print("0 - EXIT")
        print("1 - Sigmoid")
        print("2 - Tanh")
        print("3 - ReLU")
        
        act_func = int(input("> "))
        
        if act_func == 0:
            exit()
        
        if act_func == 1:
            act_func = "sigmoid"
            break
        elif act_func == 2:
            act_func = "tanh"
            break
        elif act_func == 3:
            act_func = "relu"
            break
        elif act_func == 0:
            exit()
        else:
            print("Invalid input")
    
    
    print("Enter the learning rate (default 0.1, must be float): ")
    learning_rate = float(input("> "))
    
    print("Enter momentum (default 0.0 - no momentum, enter a value between 0 and 1, i.e. 0.9): ")
    momentum = float(input("> "))
    
    print("Enter the number of epochs (default 500): ")
    epochs = int(input("> "))
    
    # set figure size for 2.8K resolution
    plt.figure(figsize=(28.8, 16.2), dpi=100)

    # init model, train and predict the values
    losses = []
    for name, (X, y) in datasets.items():
        print(f"Dataset: {name}")
        nn = NN_Model(input_size=2, hidden_size=4, output_size=1, number_of_layers=number_of_layers, learning_rate=learning_rate, func=act_func, momentum=momentum)
        losses = (nn.train(X, y, epochs=epochs))
        print("===============FINAL VALUES===============")
        print(f"Real values: {y.ravel()}")
        print(f"Predicted values: {nn.forward(X).ravel()}")
        print(f"Rounded Predicted values: {np.round(nn.forward(X).ravel())}")
        print(f"Min Loss: {min(losses)}")
        print("==========================================")
        print()
        
        plt.plot(losses, label=f'{name} Loss')
        
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training Loss for XOR, AND, OR Problem')
    # save the plot with date time
    now = datetime.datetime.now()
    plt.savefig(f"./plots/z3b_2__{now.strftime('%Y-%m-%d_%H-%M-%S')}.png")

if __name__ == "__main__":
    main()
    