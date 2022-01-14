from django.db import models


class Subscriber(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=128, unique=True)
    gdpr_consent = models.BooleanField()


class SubscriberSMS(models.Model):

    create_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=16, unique=True)
    gdpr_consent = models.BooleanField()


class Client(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=16, unique=True)
    email = models.CharField(max_length=128, unique=False)


class Users(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=16)
    email = models.CharField(max_length=128)
    gdpr_consent = models.BooleanField()
