import secrets

from django.db import transaction

from apps.students.models import (
    Parent,
    Student,
    StudentParent,
)


class RegistrationIntegrationService:
    """
    Handles synchronization requests coming from the
    CodeCamp platform.

    Responsibilities:

    - Create or reuse Parent
    - Create Student
    - Link Parent ↔ Student
    """

    @classmethod
    @transaction.atomic
    def register(cls, data):

        parent, temporary_password, parent_created = (
            cls.get_or_create_parent(data)
        )

        student = cls.create_student(
            data=data,
            parent=parent,
        )

        cls.link_parent(
            parent=parent,
            student=student,
            relationship=data["relationship"],
        )

        return {
            "student": student,
            "parent": parent,
            "temporary_password": temporary_password,
            "parent_created": parent_created,
        }

    # =====================================================
    # Parent
    # =====================================================

    @classmethod
    def get_or_create_parent(cls, data):

        parent = Parent.objects.filter(
            phone_number=data["parent_phone"]
        ).first()

        if parent:
            return parent, None, False

        temporary_password = secrets.token_urlsafe(8)

        parent = Parent(
            full_name=data["parent_name"],
            phone_number=data["parent_phone"],
            whatsapp_number=data.get(
                "parent_whatsapp",
                ""
            ),
            email=data.get(
                "parent_email",
                ""
            ),
        )

        parent.set_password(temporary_password)

        parent.save()

        return parent, temporary_password, True

    # =====================================================
    # Student
    # =====================================================

    @classmethod
    def create_student(cls, data, parent):

        student = Student.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            class_name=data["class_name"],
            parent_name=parent.full_name,
        )

        return student

    # =====================================================
    # Relationship
    # =====================================================

    @classmethod
    def link_parent(
        cls,
        parent,
        student,
        relationship,
    ):

        StudentParent.objects.get_or_create(
            parent=parent,
            student=student,
            defaults={
                "relationship": relationship,
            },
        )