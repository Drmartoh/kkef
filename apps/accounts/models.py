from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Platform identity with NGO-oriented roles."""

    class Roles(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Administrator"
        FORUM_ADMIN = "forum_admin", "Forum Administrator"
        GROUP_LEADER = "group_leader", "Group Leader"
        STAKEHOLDER = "stakeholder", "Stakeholder"
        DONOR = "donor", "Donor / Sponsor"
        MEMBER = "member", "Member"

    phone = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    role = models.CharField(
        max_length=32,
        choices=Roles.choices,
        default=Roles.MEMBER,
        db_index=True,
    )
    organization_title = models.CharField(max_length=160, blank=True)
    prefers_dark_mode = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)

    class Meta(AbstractUser.Meta):
        ordering = ["username"]

    def save(self, *args, **kwargs):
        if self.role == self.Roles.SUPER_ADMIN and not self.is_superuser:
            self.is_superuser = True
            self.is_staff = True
        super().save(*args, **kwargs)


class UserActivity(models.Model):
    """Fine-grained in-app footprint for transparency dashboards."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    action = models.CharField(max_length=96)
    target_model = models.CharField(max_length=96, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
