from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Student,
    Parent,
    StudentParent
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    def qr_preview(self, obj):

        if obj.qr_code:

            return format_html(
                '<img src="{}" width="100" />',
                obj.qr_code.url
            )

        return "-"

    qr_preview.short_description = "QR Code"
    
    readonly_fields = (
    "qr_preview",
)

    list_display = (
        "student_id",
        "first_name",
        "last_name",
        "is_active",
    )


admin.site.register(Parent)
admin.site.register(StudentParent)