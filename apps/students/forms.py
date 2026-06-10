from django import forms
from django import forms

from .models import Student


class StudentImportForm(forms.Form):

    excel_file = forms.FileField()
    

class StudentForm(forms.ModelForm):

    class Meta:

        model = Student

        fields = [

            "first_name",

            "last_name",

            "photo"

        ]