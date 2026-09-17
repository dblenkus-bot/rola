""".. Ignore pydocstyle D400."""

from rest_framework import viewsets

from rolca.core.api.permissions import IsSuperUser
from rolca.payment.api.filters import PaymentFilter
from rolca.payment.api.serializers import PaymentSerializer
from rolca.payment.models import Payment


class PaymentViewSet(viewsets.ModelViewSet):
    """API viewset for Payment objects."""

    queryset = Payment.objects.order_by("pk")
    serializer_class = PaymentSerializer
    permission_classes = (IsSuperUser,)
    filterset_class = PaymentFilter
