from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TransferDto:
    from_wallet_id: int
    to_wallet_id: int
    amount: Decimal
