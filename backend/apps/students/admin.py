from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Announcement,
    Assignment,
    Parent,
    Student,
    StudentParent,
    TeachingClass,
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
        "teaching_class",
        "is_active",
    )
    list_filter = (
        "teaching_class",
        "is_active",
    )
    search_fields = (
        "student_id",
        "first_name",
        "last_name",
        "parent_name",
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "target",
        "teaching_class",
        "class_name",
        "publish_at",
        "expires_at",
        "is_active",
    )

    list_filter = (
        "target",
        "teaching_class",
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
                    "teaching_class",
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

@admin.register(TeachingClass)
class TeachingClassAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "staff",
        "is_active",
    )
    list_filter = (
        "staff",
        "is_active",
    )
    search_fields = (
        "name",
        "staff__username",
        "staff__first_name",
        "staff__last_name",
    )


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "teaching_class",
        "due_date",
        "created_by",
        "is_active",
        "created_at",
    )
    list_filter = (
        "teaching_class",
        "is_active",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone_number",
        "email",
        "is_active",
    )
    search_fields = (
        "full_name",
        "phone_number",
        "email",
    )


@admin.register(StudentParent)
class StudentParentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "parent",
        "relationship",
        "teaching_class",
    )
    list_filter = (
        "relationship",
        "teaching_class",
    )
    search_fields = (
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "parent__full_name",
        "parent__phone_number",
    )
