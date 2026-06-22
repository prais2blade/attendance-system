from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Student
from .serializers import (
    StudentDetailSerializer
)


@api_view(["GET"])
def student_detail_api(
    request,
    student_id
):

    student = get_object_or_404(

        Student,

        student_id=student_id

    )

    serializer = (

        StudentDetailSerializer(

            student,

            context={
                "request": request
            }

        )

    )

    return Response(
        serializer.data
    )