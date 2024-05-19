# models.py

from django.db import models

class DigimartSubscription(models.Model):
    API_Key = models.CharField(max_length=255)
    API_Secret = models.CharField(max_length=255)
    API_Password = models.CharField(max_length=255)
    APP_ID = models.CharField(max_length=100)
    redirect_URL = models.URLField(max_length=255)

    def __str__(self):
        return self.APP_ID

# models.py

from django.db import models
from django.contrib.auth.models import User

class DigimartChargingSubscriberModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    STATUS_CHOICES = [
        ('Registered', 'Registered'),
        ('UnRegistered', 'UnRegistered'),
        ('UnKnown', 'UnKnown'),
    ]

    plain_msisdn = models.TextField()
    masked_msisdn = models.TextField()
    subscription_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='UnKnown')
    subscription_notification = models.TextField()
    subscription_confirm_notification = models.TextField()

    def __str__(self):
        return self.plain_msisdn


