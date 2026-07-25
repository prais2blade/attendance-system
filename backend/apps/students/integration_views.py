from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import IntegrationAuthentication
from .serializers import RegisterStudentSerializer
from .services import RegistrationIntegrationService

class RegisterStudentAPIView(APIView):

    authentication_classes = [
        IntegrationAuthentication
    ]

    permission_classes = []

    def post(self, request):

        serializer = RegisterStudentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = RegistrationIntegrationService.register(
            serializer.validated_data
        )

        return Response({

            "success": True,

            "student_id": result["student"].student_id,

            "parent_id": result["parent"].id,

            "parent_created": result["parent_created"],

            "temporary_password": result["temporary_password"],
        })