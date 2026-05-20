import json

import environ
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsForumAdminOrAbove
from apps.integrations.analytics import executive_pulse, public_transparency_cards
from apps.integrations.serializers_exports import ProposalExportPayloadSerializer

stripe = None
try:  # Soft dependency guard for environments without Stripe keys during CI.
    import stripe as stripe_sdk

    stripe = stripe_sdk
except Exception:  # pragma: no cover
    stripe = None

env = environ.Env()


class TransparencyTilesAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):  # noqa: ARG002
        return Response(public_transparency_cards())


class ExecutiveObservatoryAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, IsForumAdminOrAbove]

    def get(self, request):  # noqa: ARG002
        return Response(executive_pulse())


class ProposalPdfExportStub(APIView):
    """
    Ships structured JSON payloads for PDF engines (WeasyPrint, Gotenberg, Browserless).

    Frontend / workers can hydrate branded templates offline.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProposalExportPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "detail": "Render via your downstream PDF renderer or reuse reportlab exporters.",
                "payload": serializer.validated_data,
            }
        )


@csrf_exempt
@require_POST
def stripe_webhook(request):  # noqa: ARG001
    secret = env("STRIPE_WEBHOOK_SECRET", default="")
    if not stripe or not secret:
        return JsonResponse({"detail": "Stripe not wired."}, status=status.HTTP_501_NOT_IMPLEMENTED)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=secret)
    except ValueError:
        return JsonResponse({"detail": "Invalid payload."}, status=400)
    except Exception:  # SignatureVerificationError and SDK variance
        return JsonResponse({"detail": "Unable to verify Stripe signature."}, status=400)

    return JsonResponse({"received": True})


@csrf_exempt
@require_POST
def mpesa_callback_stub(request):
    """Capture Safaricom callbacks — validate HMAC signatures in hardened deployments."""

    try:
        envelope = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        envelope = {}

    mpesa_received = getattr(settings, "MPESA_LOGGING_ENABLED", env.bool("MPESA_LOGGING_ENABLED", default=False))
    if mpesa_received:
        from logging import getLogger

        logger = getLogger(__name__)
        logger.info("M-PESA callback envelope: %s", envelope)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


def payment_session_stub(request):  # noqa: ARG001
    return JsonResponse(
        {"detail": "Hook STRIPE_SECRET_KEY/PAYPAL keys then call respective SDKs.", "sandbox": settings.DEBUG},
    )
