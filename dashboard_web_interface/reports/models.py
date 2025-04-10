# dashboard/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Ensure the email field is unique and required
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    # Fields for email verification
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    # Track logout time (last_login is built in)
    last_logout = models.DateTimeField(blank=True, null=True)

    # Override the username field to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username is still required for admin interface

    def __str__(self):
        return self.email

class Report(models.Model):
    # Each report is linked to the user who generated it.
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    # Optionally store the report text or file info
    report_text = models.TextField(blank=True, null=True)
    downloaded = models.BooleanField(default=False)

    def __str__(self):
        return f"Report {self.pk} by {self.user.email}"
