from django import forms

from .models import Student


class StudentImportForm(forms.Form):

    excel_file = forms.FileField()


class StudentImportForm(forms.Form):

    excel_file = forms.FileField()


class StudentForm(forms.ModelForm):
    
    parent_title = forms.ChoiceField(

        required=False,

        choices=[

            ("", "---------"),

            ("Mr", "Mr"),

            ("Mrs", "Mrs"),

            ("Miss", "Miss"),

            ("Dr", "Dr"),

            ("Pastor", "Pastor"),

            ("Chief", "Chief"),

            ("Alhaji", "Alhaji"),

        ]

    )

    parent_name = forms.CharField(
        required=False,
        label="Parent Name"
    )

    parent_email = forms.EmailField(
        required=False,
        label="Parent Email"
    )

    parent_phone = forms.CharField(
        required=False,
        label="Parent Phone Number"
    )

    parent_whatsapp = forms.CharField(
        required=False,
        label="Parent WhatsApp Number"
    )

    relationship = forms.CharField(
        required=False,
        initial="Guardian",
        label="Relationship"
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            "date_of_birth"
        ].input_formats = [

            "%Y-%m-%d"

        ]

    class Meta:

        model = Student

        fields = [

            "first_name",
            "last_name",
            "photo",
            "date_of_birth",
            "gender",
            "class_name",

        ]

        widgets = {

            "date_of_birth": forms.DateInput(

                attrs={
                    "type": "date"
                },

                format="%Y-%m-%d"

            )

        }