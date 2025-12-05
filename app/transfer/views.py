from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response

from transfer.serializers import TransferSerializer
from transfer.services.transaction_service import TransactionService, TransactionError
from transfer.dto import TransferDto


class TransferAPIView(generics.CreateAPIView):
    serializer_class = TransferSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto = TransferDto(**serializer.validated_data)

        try:
            tr_s = TransactionService(dto)
            tr_s.transfer()
        except TransactionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": True})
