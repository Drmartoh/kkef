from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.integrations.services import ai_clients


class AIAssistThrottle(ScopedRateThrottle):
    scope = "burst_ai"


class ProposalDraftAssistantAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIAssistThrottle]
    throttle_scope = "burst_ai"

    def post(self, request):
        prompt = request.data.get("brief", "")
        if not prompt:
            return Response({"detail": "Provide a `brief` field."}, status=status.HTTP_400_BAD_REQUEST)

        system = (
            "You are an expert county development writer for Kiambu-Karai Empowerment Forum. "
            "Blend SDG language, community co-governance, and measurable indicators."
        )
        completion, live = ai_clients.CLIENT.complete(
            system_prompt=system,
            user_prompt=prompt[:8000],
        ), ai_clients.CLIENT.is_configured()

        if not completion:
            completion = (
                "## Executive snapshot\n"
                "- Context: {brief}\n"
                "- Theory of change: community-led monitoring + county technical assistance\n"
                "- Outcomes: livelihood resilience, environmental stewardship, gender inclusion\n"
                "- Indicators: tree cover gain, youth hours mentored, women-led contracts awarded\n"
            ).format(brief=prompt[:400])

        return Response({"draft_markdown": completion, "model_online": live})


class ReportSummarizerAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIAssistThrottle]
    throttle_scope = "burst_ai"

    def post(self, request):
        body = request.data.get("report", "")
        summary, sourced = ai_clients.summarize_text(body)
        if not summary:
            summary = (
                "Summary unavailable offline. Highlights should cover scope, disbursement discipline, "
                "participatory M&E, and environmental co-benefits once final narrative is pasted."
            )
        return Response({"summary": summary, "live_model": sourced})


class CommunityChatbotAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIAssistThrottle]
    throttle_scope = "burst_ai"

    def post(self, request):
        question = request.data.get("prompt", "")
        system = (
            "You mentor citizens on KKEF services: SACCO onboarding, watershed restoration, SACCO dashboards, "
            "county etiquette, safeguarding, GIS reporting. Keep replies concise."
        )
        answer = ai_clients.CLIENT.complete(system_prompt=system, user_prompt=question[:4000])
        if not answer:
            answer = (
                "I can clarify programmes once you specify if you represent a SACCO cluster, watershed committee, "
                "or stakeholder desk—each pathway has differentiated onboarding."
            )

        citations = [
            {"label": "Service charter", "url": "#"},
            {"label": "County GIS desk", "url": "#"},
        ]
        return Response({"reply": answer, "citations": citations})


class RecommendationEngineAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIAssistThrottle]
    throttle_scope = "burst_ai"

    def post(self, request):
        cohort = request.data.get("cluster", "community")
        playbook = []
        cohort_key = cohort.lower()

        if "fish" in cohort_key:
            playbook.append("Pair aquaculture SACCO liquidity with fisheries extension rotations.")
            playbook.append("Stage climate-smart pond profiling + IoT telemetry pilots.")
        if "women" in cohort_key:
            playbook.append("Bundle table banking with county procurement mentorship.")
        if not playbook:
            playbook.append("Sequence green enterprise grants with participatory GIS baselines.")

        playbook.append("Layer county stakeholder salons with digitally signed transparency ledgers.")

        return Response({"cohort": cohort, "recommendations": playbook})
