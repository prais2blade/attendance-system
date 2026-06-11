from .models import Notification


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