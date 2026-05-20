from decimal import Decimal

from rest_framework import serializers


class ProposalExportPayloadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    owning_group = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=64)
    narrative = serializers.CharField()
    implementation_plan = serializers.CharField(required=False, allow_blank=True)
    projected_budget = serializers.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    beneficiaries_estimate = serializers.IntegerField(min_value=0, default=0)
    sdg_tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
