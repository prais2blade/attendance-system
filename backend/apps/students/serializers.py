from rest_framework import serializers

from .models import (
    Student,
    StudentParent
)


class StudentDetailSerializer(
    serializers.ModelSerializer
):

    parent = serializers.SerializerMethodField()

    photo = serializers.SerializerMethodField()

    class Meta:

        model = Student

        fields = [

            "student_id",

            "first_name",

            "last_name",

            "class_name",

            "gender",

            "photo",

            "parent",

        ]

    def get_photo(self, obj):

        request = self.context.get(
            "request"
        )

        if obj.photo:

            return request.build_absolute_uri(
                obj.photo.url
            )

        return None

    def get_parent(self, obj):

        link = StudentParent.objects.filter(
            student=obj
        ).select_related(
            "parent"
        ).first()

        if not link:

            return None

        parent = link.parent

        return {

            "name":
                parent.full_name,

            "phone":
                parent.phone_number,

            "email":
                parent.email,

            "whatsapp":
                parent.whatsapp_number,

        }