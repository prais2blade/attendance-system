from django.urls import path

from .integration_views import RegisterStudentAPIView

from .views import (
    bulk_id_cards,
    bulk_qr_download,
    create_student,
    delete_student,
    download_student_template,
    edit_student,
    import_students,
    parent_portal,
    student_detail,
    student_id_card,
    student_list,
)

app_name = "students"

urlpatterns = [

    # ==========================================================
    # Student Management
    # ==========================================================

    path(
        "",
        student_list,
        name="student_list",
    ),

    path(
        "create/",
        create_student,
        name="create_student",
    ),

    path(
        "<int:pk>/",
        student_detail,
        name="student_detail",
    ),

    path(
        "<int:pk>/edit/",
        edit_student,
        name="edit_student",
    ),

    path(
        "<int:pk>/delete/",
        delete_student,
        name="delete_student",
    ),

    path(
        "<int:pk>/id-card/",
        student_id_card,
        name="student_id_card",
    ),

    # ==========================================================
    # Parent Portal
    # ==========================================================

    path(
        "parent/<str:token>/",
        parent_portal,
        name="parent_portal",
    ),

    # ==========================================================
    # Import / Export
    # ==========================================================

    path(
        "import/",
        import_students,
        name="import_students",
    ),

    path(
        "template/",
        download_student_template,
        name="student_template",
    ),

    path(
        "bulk-qr-download/",
        bulk_qr_download,
        name="bulk_qr_download",
    ),

    path(
        "bulk-id-cards/",
        bulk_id_cards,
        name="bulk_id_cards",
    ),

    # ==========================================================
    # CodeCamp Integration API
    # ==========================================================

    path(
        "integration/register-student/",
        RegisterStudentAPIView.as_view(),
        name="integration_register_student",
    ),
]