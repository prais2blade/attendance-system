from .models import SystemSettings


def system_settings(request):

    settings_obj = (
        SystemSettings.objects.first()
    )

    return {

        "system_settings":
            settings_obj

    }