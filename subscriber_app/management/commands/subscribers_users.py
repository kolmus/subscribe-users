from django.core.management.base import BaseCommand
from subscriber_app.models import Subscriber, Client, SubscriberSMS, Users
import csv


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Helps to migrate objects from Subscriber and SubscriberSMS models to Users
        Starts with command `$ python manage.py subscribers_users`
        Saves conflicts in csv files
        """

        users = Users.objects.all()
        subscribers = Subscriber.objects.all()
        clients = Client.objects.all()
        sms_subscribers = SubscriberSMS.objects.all()

        user_emails = []
        user_phones = []
        for user in users:
            user_emails.append(user.email)
            user_phones.append(user.phone)

        clients_phone = []
        clients_ext_phones = []
        for client in clients:
            if client.phone in clients_phone:
                # save client id, client phone in csv
                with open("subscriber_app/csv/client_conflicts.csv", mode="a") as extensions_file:
                    extension_writer = csv.writer(extensions_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    extension_writer.writerow([client.id, client.email])
                clients_ext_phones.append(client.phone)
            else:
                clients_phone.append(client.phone)

        migrated_users = []

        # Subscriber migration to Users
        for subscriber in subscribers:
            if subscriber.email in user_emails:
                continue  # to change in bonus task
            elif clients.filter(email=subscriber.email).exists():  # client.email = subscriber.email
                client = clients.filter(email=subscriber.email).first()
                if not users.filter(phone=client.phone).exclude(email=client.email).exists():  # and not(user.phone = client.phone and user.email != client.email)
                    # make new user based on client
                    if client.phone not in clients_ext_phones:
                        migrated_users.append(
                            Users(
                                phone=client.phone,
                                email=client.email,
                                gdpr_consent=False,  # most secure option => no field in model, default not set, None=False by default,
                            )
                        )

                elif users.filter(phone=client.phone).exclude(email=client.email).exists():
                    # save id and email in subscriber_conflicts.csv
                    with open("subscriber_app/csv/subscriber_conflicts.csv", mode="a") as extensions_file:
                        extension_writer = csv.writer(extensions_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        extension_writer.writerow([subscriber.id, subscriber.email])

            else:
                # make user without phone, based on subscriber
                migrated_users.append(Users(email=subscriber.email, gdpr_consent=subscriber.gdpr_consent))

        # SubscriberSMS migration to Users
        for smssubscriber in sms_subscribers:
            if smssubscriber.phone in user_phones:
                continue  # to change in bonus task

            elif clients.filter(phone=smssubscriber.phone).exists():  # client.phone = smssubscriber.phone
                client = clients.filter(phone=smssubscriber.phone).first()

                if not users.filter(email=client.email).exclude(phone=client.phone).exists():  # and not(user.email = client.email and user.phone != client.phone)
                    # make new user based on client
                    if client.phone not in clients_ext_phones:
                        migrated_users.append(
                            Users(
                                email=client.email,
                                phone=client.phone,
                                gdpr_consent=False,  # most secure option => no field in model, default not set, None=False by default,
                            )
                        )

                elif users.filter(email=client.email).exclude(phone=client.phone).exists():
                    # save id and phone in subscriber_sms_conflicts.csv
                    with open("subscriber_app/csv/subscriber_sms_conflicts.csv", mode="a") as extensions_file:
                        extension_writer = csv.writer(extensions_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        extension_writer.writerow([smssubscriber.id, smssubscriber.phone])

            else:
                # make user without email, based on subscriber
                migrated_users.append(Users(phone=smssubscriber.phone, gdpr_consent=smssubscriber.gdpr_consent))

        # Save in database
        if migrated_users:
            new_users = Users.objects.bulk_create(migrated_users, batch_size=None)  # batch_size to change if needed
            print(f"Added {len(new_users)} new_users")
        else:
            print("There is no users to migrate this time")
