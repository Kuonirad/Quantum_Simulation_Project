import torch
import torch.nn as nn

# Ensure CUDA is available for GPU acceleration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"QHR Model using device: {device}")

class QHRModel(nn.Module):
    """
    A simple LSTM-based model for predicting quantum state evolution.
    Note: This model is a placeholder and has not been trained with physical
    constraints, as noted in the README.
    """
    def __init__(self, input_size, hidden_size, output_size):
        super(QHRModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # Move input to the appropriate device
        x = x.to(device)
        lstm_out, _ = self.lstm(x)
        # We only need the output of the last time step
        last_output = lstm_out[:, -1, :]
        return self.fc(last_output)
