from .models import Notification

from .services import (
    send_notification_email
)


def process_pending_notifications():

    notifications = Notification.objects.filter(

        status="pending",

        channel="email"

    )

    for notification in notifications:

        send_notification_email(
            notification
        )