from .models import Notification
from django.core.mail import send_mail
from django.utils import timezone



def create_notification(

    recipient,
    channel,
    subject,
    message

):

    return Notification.objects.create(

        recipient=recipient,

        channel=channel,

        subject=subject,

        message=message,

        status="pending"

    )
    


def send_notification_email(notification):

    try:

        send_mail(

            subject=notification.subject,

            message=notification.message,

            from_email=None,

            recipient_list=[
                notification.recipient
            ],

            fail_silently=False

        )

        notification.status = "sent"

        notification.sent_at = timezone.now()

        notification.save(

            update_fields=[
                "status",
                "sent_at"
            ]

        )

        return True

    except Exception:

        notification.status = "failed"

        notification.save(

            update_fields=[
                "status"
            ]

        )

        return False
    
    
def send_whatsapp_message(

    phone_number,

    message

):

    print(

        f"WhatsApp => "

        f"{phone_number}"

    )

    print(message)

    return True