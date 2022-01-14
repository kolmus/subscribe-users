from django.core.management.base import BaseCommand
from django.db.models import Q

from subscriber_app.models import Subscriber, Client, SubscriberSMS, Users


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Updates Users gdpr_consent in necessary objects"""
        users = Users.objects.all()
        subscribers = Subscriber.objects.all()
        sms_subscribers = SubscriberSMS.objects.all()

        sub_emails = []
        for sub in subscribers:
            sub_emails.append(sub.email)

        subsms_phones = []
        for subsms in sms_subscribers:
            sub_emails.append(subsms.phone)

        users_to_update = []
        for user in users.filter(Q(email__in=sub_emails) | Q(phone__in=subsms_phones)):
            # exists subscriber and subscriber_sms
            if user.email in sub_emails and user.phone in subsms_phones:
                subscriber = subscribers.get(email=user.email)
                subscriber_sms = sms_subscribers.get(phone=user.phone)
                # check if udate is necessary
                if user.gdpr_consent == subscriber.gdpr_consent and user.gdpr_consent == subscriber_sms.gdpr_consent:
                    continue
                # check newer
                if subscriber.create_date > subscriber_sms.create_date and subscriber.gdpr_consent != user.gdpr_consent:
                    user.gdpr_consent = subscriber.gdpr_consent
                    users_to_update.append(user)
                if subscriber.create_date < subscriber_sms.create_date and subscriber_sms.gdpr_consent != user.gdpr_consent:
                    user.gdpr_consent = subscriber_sms.gdpr_consent
                    users_to_update.append(user)

            # exist just subscriber
            elif user.email in sub_emails:
                subscriber = subscribers.get(email=user.email)
                # check if udate is necessary
                if user.gdpr_consent == subscriber.gdpr_consent:
                    continue
                if user.create_date < subscriber.create_date:
                    user.gdpr_consent = subscriber.gdpr_consent
                    users_to_update.append(user)

            # exist just subscriber_sms
            elif user.phone in subsms_phones:
                subscriber_sms = sms_subscribers.get(phone=user.phone)
                # check if udate is necessary
                if user.gdpr_consent == subscriber_sms.gdpr_consent:
                    continue
                if user.create_date < subscriber_sms.create_date:
                    user.gdpr_consent = subscriber_sms.gdpr_consent
                    users_to_update.append(user)
        # update db
        if users_to_update:
            updates = Users.objects.bulk_update(users_to_update, ["gdpr_consent"], batch_size=None)  # batch_size to change if needed
            print(f"{updates} has been updated!\n")
        else:
            print("No updates this time")
