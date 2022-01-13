from django.shortcuts import render
from django.views import View

from .models import Subscriber, SubscriberSMS, Client, Users


class SubscriberList(View):
    def get(self, request):
        list = Subscriber.objects.all()
        return render(request, 'subscriber_app/index.html', {'list': list})


class SubscriberSMSList(View):
    def get(self, request):
        list = SubscriberSMS.objects.all()
        return render(request, 'subscriber_app/index.html', {'list': list})


class ClientList(View):
    def get(self, request):
        list = Client.objects.all()
        return render(request, 'subscriber_app/index.html', {'list': list})


class UsersList(View):
    def get(self, request):
        list = Users.objects.all()
        return render(request, 'subscriber_app/index.html', {'list': list})

# class SubscriberTooUsers(View)
