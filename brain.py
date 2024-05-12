import numpy as np


class NeuralBrain:

    def __init__(self, input_size=12, hidden_sizes=None, output_size=12, output_activation='relu'):
        if hidden_sizes is None:
            hidden_sizes = [48, 96, 96, 48, 24]
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        self.output_activation = output_activation

        # Initialize weights and biases randomly
        self.weights = []
        self.biases = []
        prev_size = input_size
        for hidden_size in hidden_sizes:
            self.weights.append(np.random.randn(prev_size, hidden_size))
            self.biases.append(np.random.randn(hidden_size))
            prev_size = hidden_size
        self.weights.append(np.random.randn(prev_size, output_size))
        self.biases.append(np.random.randn(output_size))

    def forward(self, inputs):
        # Forward pass through the neural network
        activations = inputs

        for weights, bias in zip(self.weights[:-1], self.biases[:-1]):
            activations = np.dot(activations, weights) + bias
            activations = self.relu(activations)  # ReLU activation for hidden layers
        outputs = np.dot(activations, self.weights[-1]) + self.biases[-1]
        outputs = self.activation_function(outputs)  # Activation function for output layer
        return outputs

    def mutate(self, mutation_rate):
        layer_idx = np.random.randint(len(self.weights))

        # Mutate weights of the selected layer
        weights_mask = np.random.rand(*self.weights[layer_idx].shape) < mutation_rate
        self.weights[layer_idx][weights_mask] = np.random.randn(*self.weights[layer_idx][weights_mask].shape)

        # Mutate biases of the selected layer
        biases_mask = np.random.rand(self.biases[layer_idx].shape[0]) < mutation_rate
        self.biases[layer_idx][biases_mask] = np.random.randn(len(self.biases[layer_idx][biases_mask]))

    def relu(self, x):
        return np.maximum(0, x)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def tanh(self, x):
        return np.tanh(x)

    def sin(self, x):
        return np.sin(x)

    def activation_function(self, x):
        # Select the activation function based on the specified output_activation
        if self.output_activation == 'relu':
            return self.relu(x)
        elif self.output_activation == 'sigmoid':
            return self.sigmoid(x)
        elif self.output_activation == 'tanh':
            return self.tanh(x)
        elif self.output_activation == 'sin':
            return self.sin(x)
        else:
            raise ValueError(f"Invalid output activation function: {self.output_activation}")
