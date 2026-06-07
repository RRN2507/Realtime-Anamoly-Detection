import torch
import torch.nn as nn
import numpy as np

class TransactionLSTM(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=32, num_layers=2):
        super(TransactionLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_dim, input_dim)
        
    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        out, _ = self.lstm(x)
        # We want to predict the next value in the sequence
        out = self.linear(out)
        return out

def save_dummy_model(path="spark-job/model.pth"):
    model = TransactionLSTM()
    torch.save(model.state_dict(), path)
    print(f"Dummy LSTM model saved to {path}")

if __name__ == "__main__":
    save_dummy_model()
