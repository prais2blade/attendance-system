from rest_framework import serializers

from .models import (
    Student,
    StudentParent,
    Parent
)
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication


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


class StudentListSerializer(
    serializers.ModelSerializer
):

    photo = serializers.SerializerMethodField()

    parent_name = serializers.SerializerMethodField()

    class Meta:

        model = Student

        fields = [

            "student_id",

            "first_name",

            "last_name",

            "class_name",

            "gender",

            "photo",

            "parent_name",

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

    def get_parent_name(self, obj):

        link = StudentParent.objects.filter(
            student=obj
        ).select_related(
            "parent"
        ).first()

        if not link:

            return "N/A"

        return link.parent.full_name
    

class ParentLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()
    
    

class ParentChildSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.CharField()
    full_name = serializers.CharField()
    class_name = serializers.CharField()
    attendance_today = serializers.BooleanField()
    
    
class ParentJWTAuthentication(JWTAuthentication):
    """
    Authenticate Parent using JWT.
    The JWT contains:
        parent_id
        phone
    """

    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            return None

        raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        parent_id = validated_token.get("parent_id")

        if not parent_id:
            raise exceptions.AuthenticationFailed(
                "Invalid parent token."
            )

        try:
            parent = Parent.objects.get(id=parent_id)

        except Parent.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "Parent account not found."
            )

        return (parent, validated_token)
    
    
class RegisterStudentSerializer(serializers.Serializer):

    first_name = serializers.CharField(max_length=100)

    last_name = serializers.CharField(max_length=100)

    parent_name = serializers.CharField(max_length=200)

    parent_phone = serializers.CharField(max_length=20)

    parent_whatsapp = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )

    parent_email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    relationship = serializers.CharField()

    class_name = serializers.CharField()

    mode = serializers.CharField()

    registration_code = serializers.CharField()

    camp_year = serializers.IntegerField()

    program = serializers.CharField()
    