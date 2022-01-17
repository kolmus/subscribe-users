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
        clients = Client.objects.all()

        user_emails = set()
        user_phones = set()
        for user in users:
            user_emails.add(user.email)
            user_phones.add(user.phone)

        clients_phone = set()
        clients_ext_phones = []
        for client in clients:
            if client.phone in clients_phone:
                # save client id, client phone in csv
                with open("subscriber_app/csv/client_conflicts.csv", mode="a") as extensions_file:
                    extension_writer = csv.writer(extensions_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    extension_writer.writerow([client.id, client.email])
                clients_ext_phones.append(client.phone)
            else:
                clients_phone.add(client.phone)

        migrated_users = []

        subscribers = Subscriber.objects.all().exclude(email__in=user_emails)
        # Subscriber migration to Users
        for subscriber in subscribers:
            # client.email = subscriber.email
            if clients.filter(email=subscriber.email).exists():
                client = clients.filter(email=subscriber.email).first()
                # and not(user.phone = client.phone and user.email != client.email)
                if not users.filter(phone=client.phone).exclude(email=client.email).exists():
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

        sms_subscribers = SubscriberSMS.objects.all().exclude(phone__in=user_phones)
        # SubscriberSMS migration to Users
        for smssubscriber in sms_subscribers:
            # client.phone = smssubscriber.phone
            if clients.filter(phone=smssubscriber.phone).exists():
                client = clients.get(phone=smssubscriber.phone)

                # and not(user.email = client.email and user.phone != client.phone)
                if not users.filter(email=client.email).exclude(phone=client.phone).exists():
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
