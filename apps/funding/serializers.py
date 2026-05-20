from rest_framework import serializers

from apps.funding.models import Donation, Sponsor


class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = "__all__"


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "stripe_session_id",
            "stripe_payment_intent_id",
            "paypal_order_id",
            "mpesa_checkout_request_id",
            "mpesa_receipt",
            "status",
            "reference",
        )
