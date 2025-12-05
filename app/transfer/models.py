from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django_extended.models import BaseModel
from django_extended.enums import TransactionStatusType


class Wallet(BaseModel):
    owner = models.CharField(max_length=255, blank=True, null=True, unique=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    currency = models.CharField(
        default="u",
        max_length=3,
        choices=[(x, x) for x in settings.CURRENCIES],
    )

    def __str__(self):
        return f"Wallet({self.id}, owner={self.owner}, balance={self.balance})"

    def clean(self):
        if self.balance < Decimal("0.0") and self.balance != Decimal("0.0"):
            raise ValidationError({"balance": "The balance must be positive"})
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Transaction(BaseModel):
    to_wallet = models.ForeignKey(
        Wallet, related_name="incoming", on_delete=models.SET_NULL, null=True
    )
    from_wallet = models.ForeignKey(
        Wallet, related_name="outgoing", on_delete=models.SET_NULL, null=True
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    commission = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_debit = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=[(s.value, s.name.title()) for s in TransactionStatusType],
        default=TransactionStatusType.PENDING.value,
    )

    def __str__(self):
        return f"Transaction({self.id}, {self.from_wallet_id} -> {self.to_wallet_id}, {self.amount})"
