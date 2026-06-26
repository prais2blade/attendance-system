from .models import Parent
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Parent


def get_parent_from_token(request):

    token = request.auth

    if not token:
        return None

    parent_id = token.get("parent_id")

    if not parent_id:
        return None

    try:
        return Parent.objects.get(id=parent_id)
    except Parent.DoesNotExist:
        return None
    

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