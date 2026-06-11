from django.utils import timezone

from apps.students.models import StudentParent

from .services import create_notification


def notify_check_in(student, timestamp):

    parents = StudentParent.objects.filter(
        student=student
    )

    for link in parents:

        parent = link.parent

        greeting = (

            f"{parent.title} {parent.full_name}"

            if parent.title

            else parent.full_name

        )

        today = timestamp.date()

        check_in_time = timestamp.strftime(
            "%I:%M %p"
        )

        message = f"""
Dear {greeting},

This is to inform you that
{student.first_name} {student.last_name}
has successfully checked in to
CodeCamp Innovation Hub.

Date: {today}
Time: {check_in_time}

Please be assured that they are in safe hands.

Thank you.

CodeCamp Innovation Hub
"""

        if parent.email:

            create_notification(

                recipient=parent.email,

                channel="email",

                subject="Student Check-In",

                message=message

            )


def notify_check_out(student, timestamp):

    parents = StudentParent.objects.filter(
        student=student
    )

    for link in parents:

        parent = link.parent

        greeting = (

            f"{parent.title} {parent.full_name}"

            if parent.title

            else parent.full_name

        )

        today = timestamp.date()

        check_out_time = timestamp.strftime(
            "%I:%M %p"
)

        message = f"""
Dear {greeting},

This is to inform you that
{student.first_name} {student.last_name}
has successfully checked out from
CodeCamp Innovation Hub.

Date: {today}
Time: {check_out_time}

We hope they had a great day at the hub and we look forward to seeing them again soon.

Thank you.

CodeCamp Innovation Hub
"""

        if parent.email:

            create_notification(

                recipient=parent.email,

                channel="email",

                subject="Student Check-Out",

                message=message

            )