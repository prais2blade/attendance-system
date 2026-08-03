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


from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "target",
        "class_name",
        "publish_at",
        "expires_at",
        "is_active",
    )

    list_filter = (
        "target",
        "is_active",
        "publish_at",
    )

    search_fields = (
        "title",
        "message",
        "class_name",
    )

    ordering = (
        "-publish_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Announcement",
            {
                "fields": (
                    "title",
                    "message",
                ),
            },
        ),

        (
            "Audience",
            {
                "fields": (
                    "target",
                    "class_name",
                ),
            },
        ),

        (
            "Attachment",
            {
                "fields": (
                    "attachment",
                ),
            },
        ),

        (
            "Publication",
            {
                "fields": (
                    "is_active",
                    "publish_at",
                    "expires_at",
                ),
            },
        ),

        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),

    )

    actions = (
        "activate_announcements",
        "deactivate_announcements",
    )

    @admin.action(
        description="Activate selected announcements"
    )
    def activate_announcements(
        self,
        request,
        queryset,
    ):
        queryset.update(
            is_active=True,
        )

    @admin.action(
        description="Deactivate selected announcements"
    )
    def deactivate_announcements(
        self,
        request,
        queryset,
    ):
        queryset.update(
            is_active=False,
        )

admin.site.register(Parent)
admin.site.register(StudentParent)