from django import forms
from django.core.exceptions import ValidationError

from apps.funding.models import DonorIntake
from apps.organizations.models import GroupJoinApplication

_INPUT = (
    "mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm "
    "text-slate-900 shadow-inner focus:border-forest focus:outline-none focus:ring-1 focus:ring-forest/30 "
    "dark:border-white/10 dark:bg-[#070d18] dark:text-white"
)
_CHECK = "mt-1 h-4 w-4 shrink-0 rounded border-slate-300 text-forest focus:ring-forest/40"


class DonorIntakeForm(forms.ModelForm):
    agree_contact = forms.BooleanField(
        required=True,
        label="I understand that KKEF may contact me using the details I provide to complete this gift or inquiry.",
    )

    class Meta:
        model = DonorIntake
        fields = (
            "kind",
            "amount",
            "currency",
            "payment_preference",
            "resource_category",
            "resource_description",
            "quantity_or_estimate",
            "message_subject",
            "message_body",
            "attachment",
            "display_name",
            "email",
            "phone",
            "anonymous",
        )
        widgets = {
            "kind": forms.RadioSelect,
            "amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Amount in KES",
                    "class": _INPUT,
                }
            ),
            "currency": forms.Select(attrs={"class": _INPUT}),
            "payment_preference": forms.TextInput(
                attrs={
                    "placeholder": "M-Pesa, bank transfer, card, visit office…",
                    "class": _INPUT,
                }
            ),
            "resource_category": forms.Select(attrs={"class": _INPUT}),
            "resource_description": forms.Textarea(
                attrs={"rows": 4, "class": _INPUT, "placeholder": "Describe items, condition, and how you can deliver or hand over."}
            ),
            "quantity_or_estimate": forms.TextInput(
                attrs={
                    "placeholder": "e.g. 200 seedlings, 20 balls, one lorry load",
                    "class": _INPUT,
                }
            ),
            "message_subject": forms.TextInput(
                attrs={"placeholder": "Optional subject line", "class": _INPUT}
            ),
            "message_body": forms.Textarea(
                attrs={
                    "rows": 6,
                    "class": _INPUT,
                    "placeholder": "Your letter, proposal summary, or questions for the forum…",
                }
            ),
            "attachment": forms.ClearableFileInput(
                attrs={
                    "accept": ".pdf,.doc,.docx,.txt",
                    "class": _INPUT
                    + " file:mr-3 file:rounded-lg file:border-0 file:bg-forest file:px-3 file:py-2 file:text-xs file:font-semibold file:text-white",
                }
            ),
            "display_name": forms.TextInput(attrs={"placeholder": "Your full name", "class": _INPUT}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "class": _INPUT}),
            "phone": forms.TextInput(attrs={"placeholder": "Optional", "class": _INPUT}),
            "anonymous": forms.CheckboxInput(attrs={"class": _CHECK}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["agree_contact"].widget.attrs.setdefault("class", _CHECK)
        self.fields["currency"].choices = [("KES", "KES — Kenyan Shilling"), ("USD", "USD — US Dollar (convert locally)")]

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get("kind")
        anonymous = cleaned.get("anonymous")
        email = (cleaned.get("email") or "").strip()
        name = (cleaned.get("display_name") or "").strip()

        if anonymous:
            cleaned["display_name"] = ""
        elif not name:
            raise ValidationError("Please enter your name, or tick “Give anonymously”.")

        if kind == DonorIntake.Kind.MONEY:
            amount = cleaned.get("amount")
            if amount is None or amount <= 0:
                raise ValidationError({"amount": "Enter the amount you wish to give (KES)."})
            if not email:
                raise ValidationError({"email": "Email is required so we can confirm your contribution."})
        elif kind == DonorIntake.Kind.RESOURCES:
            if not cleaned.get("resource_category"):
                raise ValidationError({"resource_category": "Select the type of resources you are offering."})
            if not (cleaned.get("resource_description") or "").strip():
                raise ValidationError({"resource_description": "Describe the resources you wish to donate."})
            if not email and not cleaned.get("phone"):
                raise ValidationError(
                    "Please provide an email or phone number so our team can coordinate collection or delivery."
                )
        elif kind == DonorIntake.Kind.MESSAGE:
            if not (cleaned.get("message_body") or "").strip():
                raise ValidationError({"message_body": "Please write your message, proposal summary, or inquiry."})
            if not email:
                raise ValidationError({"email": "Email is required so we can respond to your letter or proposal."})

        cleaned["email"] = email
        return cleaned

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            return None
        if amount < 0:
            raise ValidationError("Amount cannot be negative.")
        return amount


class GroupJoinApplicationForm(forms.ModelForm):
    class Meta:
        model = GroupJoinApplication
        fields = (
            "certificate_number",
            "group_name",
            "phone",
            "chairperson_name",
            "group_type",
            "ward",
            "contact_email",
        )
        widgets = {
            "group_name": forms.TextInput(
                attrs={"placeholder": "Registered name of your group", "class": _INPUT}
            ),
            "phone": forms.TextInput(attrs={"placeholder": "e.g. 07XXXXXXXX", "class": _INPUT}),
            "chairperson_name": forms.TextInput(
                attrs={"placeholder": "Chairperson or lead contact", "class": _INPUT}
            ),
            "certificate_number": forms.TextInput(
                attrs={"placeholder": "Certificate or registration number (unique)", "class": _INPUT}
            ),
            "group_type": forms.Select(attrs={"class": _INPUT}),
            "ward": forms.Select(attrs={"class": _INPUT}),
            "contact_email": forms.EmailInput(attrs={"placeholder": "Optional", "class": _INPUT}),
        }

    def clean_certificate_number(self):
        raw = self.cleaned_data.get("certificate_number", "")
        normalized = "".join(raw.strip().upper().split())
        if len(normalized) < 3:
            raise ValidationError("Enter a valid certificate or registration number.")
        if GroupJoinApplication.objects.filter(pk=normalized).exists():
            raise ValidationError(
                "An application with this certificate or registration number is already on file. "
                "If you need to update it, please email the secretariat."
            )
        return normalized
