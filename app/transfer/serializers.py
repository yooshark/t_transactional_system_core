from typing import Any

from rest_framework import serializers
from rest_framework.serializers import ValidationError


class TransferSerializer(serializers.Serializer):
    from_wallet_id = serializers.IntegerField()
    to_wallet_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0.01)

    def validate(self, attrs) -> dict[str, Any]:
        if attrs["from_wallet_id"] == attrs["to_wallet_id"]:
            raise ValidationError({"detail": "from and to must differ"})
        return attrs
