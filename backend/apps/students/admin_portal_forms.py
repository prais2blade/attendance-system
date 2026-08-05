from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.crypto import get_random_string

from .models import Student, TeachingClass


FIELD_CLASS = (
    "w-full rounded-lg border border-slate-300 px-4 py-3 "
    "outline-none focus:border-emerald-700 focus:ring-2 "
    "focus:ring-emerald-100"
)
CHECKBOX_CLASS = (
    "h-4 w-4 rounded border-slate-300 text-emerald-700 "
    "focus:ring-emerald-600"
)


def apply_widget_classes(fields):
    for field in fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.setdefault("class", CHECKBOX_CLASS)
        else:
            field.widget.attrs.setdefault("class", FIELD_CLASS)


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "class": FIELD_CLASS,
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": FIELD_CLASS,
            }
        ),
    )


class StaffUserCreateForm(forms.ModelForm):
    generated_password = None

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_widget_classes(self.fields)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = get_user_model().TEACHER
        user.is_staff = False
        user.staff_must_change_password = True
        self.generated_password = generate_staff_temporary_password()
        user.set_password(self.generated_password)

        if commit:
            user.save()

        return user


def generate_staff_temporary_password():
    return f"Staff-{get_random_string(8)}-9"


class TeachingClassAdminForm(forms.ModelForm):
    class Meta:
        model = TeachingClass
        fields = [
            "name",
            "description",
            "staff",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        User = get_user_model()
        staff_filter = Q(
            role=User.TEACHER,
            is_active=True,
        )

        if self.instance and self.instance.staff_id:
            staff_filter |= Q(pk=self.instance.staff_id)

        self.fields["staff"].queryset = User.objects.filter(
            staff_filter,
        ).order_by("first_name", "last_name", "username")
        self.fields["staff"].required = False

        apply_widget_classes(self.fields)


class StudentClassAssignmentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "teaching_class",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teaching_class"].queryset = TeachingClass.objects.filter(
            is_active=True,
        ).order_by("name")
        self.fields["teaching_class"].required = False

        apply_widget_classes(self.fields)

    def save(self, commit=True):
        student = super().save(commit=False)

        if student.teaching_class:
            student.class_name = student.teaching_class.name
        else:
            student.class_name = ""

        if commit:
            student.save()

        return student
