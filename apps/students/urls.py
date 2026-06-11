from django.urls import path

from .views import (
    student_detail,
    student_id_card,
    parent_portal,
    import_students,
    student_list,
    create_student,
    edit_student,
    delete_student,
    bulk_qr_download,
    bulk_id_cards,
    download_student_template,
)

urlpatterns = [
    path(
        "<int:pk>/",
        student_detail,
        name="student_detail"
    ),
    path("<int:pk>/id-card/", student_id_card, name="student_id_card"),
    path(
    "parent/<str:token>/",
    parent_portal,
    name="parent_portal"
),

path(
    "import/",
    import_students,
    name="import_students"
),
path(
    "",
    student_list,
    name="student_list"
),
path(
    "create/",
    create_student,
    name="create_student"
),
path(
    "<int:pk>/edit/",
    edit_student,
    name="edit_student"
),
path(
    "<int:pk>/delete/",
    delete_student,
    name="delete_student"
),
path(
    "bulk-qr-download/",
    bulk_qr_download,
    name="bulk_qr_download"
),
path(
    "bulk-id-cards/",
    bulk_id_cards,
    name="bulk_id_cards"
),
path(
    "template/",
    download_student_template,
    name="student_template"
),
path(
    "template/",
    download_student_template,
    name="student_template"
),
]