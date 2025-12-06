from django.contrib import admin
from django.contrib.admin import ModelAdmin

from transfer.models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    pass
