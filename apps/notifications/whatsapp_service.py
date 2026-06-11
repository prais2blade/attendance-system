import urllib.parse


def build_whatsapp_url(

    phone_number,

    message

):

    phone_number = (
        phone_number
        .replace("+", "")
        .replace(" ", "")
    )

    encoded_message = urllib.parse.quote(
        message
    )

    return (
        f"https://wa.me/"
        f"{phone_number}"
        f"?text={encoded_message}"
    )