# =============================================================
#  共通のPyTorchモデル定義（各スクリプトから import して使う）
#
#  タクシー特徴量から totalAmount を予測する小さな MLP。
#  「モデル本体は PyTorch、大規模データの並列処理は Spark」という
#  役割分担を示すための共通部品。
# =============================================================
import torch
import torch.nn as nn

FEATURES = ["tripDistance", "passengerCount", "durationMin"]


class FarePredictor(nn.Module):
    def __init__(self, in_dim=3, hidden=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def build_model(seed=0):
    """再現性のため固定シードで初期化したモデルを返す。"""
    torch.manual_seed(seed)
    return FarePredictor()
