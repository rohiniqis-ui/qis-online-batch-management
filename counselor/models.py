from django.db import models
from django.conf import settings


class CounselorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username