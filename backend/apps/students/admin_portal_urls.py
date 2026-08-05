from django.urls import path

from .admin_portal_views import (
    admin_class_create,
    admin_class_edit,
    admin_class_list,
    admin_dashboard,
    admin_login,
    admin_logout,
    admin_staff_create,
    admin_staff_list,
    admin_student_assign_class,
    admin_student_list,
)


app_name = "school_admin"

urlpatterns = [
    path(
        "login/",
        admin_login,
        name="login",
    ),
    path(
        "logout/",
        admin_logout,
        name="logout",
    ),
    path(
        "",
        admin_dashboard,
        name="dashboard",
    ),
    path(
        "staff/",
        admin_staff_list,
        name="staff_list",
    ),
    path(
        "staff/create/",
        admin_staff_create,
        name="staff_create",
    ),
    path(
        "classes/",
        admin_class_list,
        name="class_list",
    ),
    path(
        "classes/create/",
        admin_class_create,
        name="class_create",
    ),
    path(
        "classes/<int:class_id>/edit/",
        admin_class_edit,
        name="class_edit",
    ),
    path(
        "students/",
        admin_student_list,
        name="student_list",
    ),
    path(
        "students/<int:student_id>/assign-class/",
        admin_student_assign_class,
        name="student_assign_class",
    ),
]
