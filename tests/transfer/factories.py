import factory
from decimal import Decimal

from django_extended.enums import TransactionStatusType
from transfer.models import Wallet, Transaction


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wallet

    owner = factory.Sequence(lambda n: f"user{n}")
    balance = Decimal("1000.00")
    currency = "u"


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    from_wallet = factory.SubFactory(WalletFactory)
    to_wallet = factory.SubFactory(WalletFactory)
    amount = Decimal("100.00")
    commission = Decimal("0.00")
    total_debit = factory.LazyAttribute(lambda o: o.amount + o.commission)
    status = TransactionStatusType.SUCCESS.value
