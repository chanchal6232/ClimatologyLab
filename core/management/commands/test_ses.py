from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends a test email via AWS SES'

    def handle(self, *args, **options):
        self.stdout.write("Attempting to send test email via SES API...")
        try:
            subject = 'AWS SES Test - Climatology Lab'
            message = 'This is a test email to verify that the AWS SES API integration is working correctly.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.ADMIN_EMAIL]

            self.stdout.write(f"From: {from_email}")
            self.stdout.write(f"To: {recipient_list}")

            send_mail(subject, message, from_email, recipient_list)
            self.stdout.write(self.style.SUCCESS('SUCCESS: Test email sent!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'FAILED: {str(e)}'))
