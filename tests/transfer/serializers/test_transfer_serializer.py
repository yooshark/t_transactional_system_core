import pytest
from rest_framework.serializers import ValidationError

from transfer.serializers import TransferSerializer
from django_extended.constants import MINIMUM_TRANSFER_RATE


class TestTransferSerializer:
    def test_it_serializes_valid_data(self):
        data = {
            "from_wallet_id": 1,
            "to_wallet_id": 2,
            "amount": str(MINIMUM_TRANSFER_RATE + 10),
        }

        serializer = TransferSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        expected = {
            "from_wallet_id": 1,
            "to_wallet_id": 2,
            "amount": MINIMUM_TRANSFER_RATE + 10,
        }
        assert serializer.validated_data == expected

    def test_it_raises_error_if_wallets_are_equal(self):
        data = {
            "from_wallet_id": 5,
            "to_wallet_id": 5,
            "amount": str(MINIMUM_TRANSFER_RATE + 1),
        }

        serializer = TransferSerializer(data=data)

        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        assert "from and to must differ" in str(exc.value)

    def test_it_raises_error_if_amount_is_too_small(self):
        data = {
            "from_wallet_id": 1,
            "to_wallet_id": 2,
            "amount": "0.01",
        }

        serializer = TransferSerializer(data=data)

        assert serializer.is_valid() is False
        assert "amount" in serializer.errors

    def test_it_raises_error_if_missing_fields(self):
        serializer = TransferSerializer(data={})

        assert serializer.is_valid() is False
        assert "from_wallet_id" in serializer.errors
        assert "to_wallet_id" in serializer.errors
        assert "amount" in serializer.errors

    def test_it_raises_error_if_amount_not_decimal(self):
        data = {
            "from_wallet_id": 1,
            "to_wallet_id": 2,
            "amount": "invalid",
        }

        serializer = TransferSerializer(data=data)

        assert serializer.is_valid() is False
        assert "amount" in serializer.errors

    def test_it_raises_error_if_wallet_ids_not_int(self):
        data = {
            "from_wallet_id": "abc",
            "to_wallet_id": "xyz",
            "amount": str(MINIMUM_TRANSFER_RATE + 1),
        }

        serializer = TransferSerializer(data=data)

        assert serializer.is_valid() is False
        assert "from_wallet_id" in serializer.errors
        assert "to_wallet_id" in serializer.errors
