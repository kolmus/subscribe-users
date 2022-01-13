from django.core.management.base import BaseCommand
from subscriber_app.models import Subscriber, Client, Users
import csv

class Command(BaseCommand):
    def handle(self, *args, **options):
        """Helps to migrate Subscribers to Users
        """        
        users = Users.objects.all()
        subscribers = Subscriber.objects.all()
        clients = Client.objects.all()
        
        user_emails = []
        for user in users:
            user_emails.append(user.email)
        
        clients_phone = []
        clients_ext_phones = []
        for client in clients:
            if client.phone in clients_phone:
                # save client id, client phone in csv
                with open('client_conflicts.csv', mode='w') as extensions_file:
                        extension_writer = csv.writer(extensions_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        extension_writer.writerow([client.id, client.email])
                clients_ext_phones.append(client.phone)
            else:
                clients_phone.append(client.phone)
        
        # Subscriber migration to Users
        for subscriber in subscribers:
            if subscriber.email in user_emails:
                continue             # to change in bonus task
            elif clients.filter(email=subscriber.email).exists:         # client.email = subscriber.email
                client = clients.filter(email=subscriber.email).first()
                
                if not users.filter(phone=client.phone).exclude(email=client.email).exists():       # and not(user.phone = client.phone and user.email != client.email)
                    # make new user based on client
                    if client.phone not in clients_ext_phones:
                        new_user = Users()
                        new_user.phone = client.phone
                        new_user.email = client.email
                        new_user.gdpr_consent = False       # most secure option => no field in model, default not set, None=False by default,
                        new_user.save()
                
                elif users.filter(phone=client.phone).exclude(email=client.email).exists():
                    # save id and email in subscriber_conflicts.csv
                    with open('subscriber_conflicts.csv', mode='w') as extensions_file:
                        extension_writer = csv.writer(extensions_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        extension_writer.writerow([subscriber.id, subscriber.email])
            
            else:
                # make user without phone, based on subscriber
                new_user = Users() 
                new_user.email = subscriber.email
                new_user.gdpr_consent = subscriber.gdpr_consent
                new_user.save()
            
