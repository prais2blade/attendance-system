from apps.students.models import StudentParent
from .services import create_notification


def notify_check_in(student):

    parents = StudentParent.objects.filter(
        student=student
    )

    for link in parents:

        parent = link.parent

        if parent.email:

            create_notification(

                recipient=parent.email,

                channel="email",

                subject="Student Check-In",

                message=(
                    f"{student.first_name} "
                    f"{student.last_name} "
                    f"has checked in."
                )

            )


def notify_check_out(student):

    parents = StudentParent.objects.filter(
        student=student
    )

    for link in parents:

        parent = link.parent

        if parent.email:

            create_notification(

                recipient=parent.email,

                channel="email",

                subject="Student Check-Out",

                message=(
                    f"{student.first_name} "
                    f"{student.last_name} "
                    f"has checked out."
                )

            )