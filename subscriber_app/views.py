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

class SubscriberToUsers(View):
    def post(self, request):

        users = Users.objects.all()
        subscribers = Subscriber.objects.all()
        clients = Client.objects.all()
        
        user_emails = []
        for user in users:
            user_emails.append(user.email)

        for subscriber in subscribers:
            if subscriber.email in user_emails:
                continue             # to change in bonus task
            
            elif clients.filter(email=subscriber.email).exists:         # client.email = subscriber.email
                client = clients.filter(email=subscriber.email).first()
                
                if not users.filter(phone=client.phone).exclude(email=client.email).exists():                     # and not(user.phone = client.phone and user.email != client.email)
                    # make new user based on client
                elif users.filter(phone=client.phone).exclude(email=client.email).exists():
                    # save id and email in subscriber_conflicts.csv
            else:
                # make user without phone, based on subscriber
        
        
# https://realpython.com/python-csv/