from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from apps.attendance.models import Attendance

from .admin_auth import admin_required, is_admin_portal_user
from .admin_portal_forms import (
    AdminLoginForm,
    StaffUserCreateForm,
    StudentClassAssignmentForm,
    TeachingClassAdminForm,
)
from .models import Assignment, Student, StudentParent, TeachingClass


def admin_login(request):
    if is_admin_portal_user(request.user):
        return redirect("school_admin:dashboard")

    form = AdminLoginForm()
    next_url = request.GET.get("next") or request.POST.get("next") or ""

    if request.method == "POST":
        form = AdminLoginForm(request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            if user and is_admin_portal_user(user):
                login(request, user)

                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)

                return redirect("school_admin:dashboard")

            messages.error(
                request,
                "Invalid admin login details.",
            )

    return render(
        request,
        "admin_portal/login.html",
        {
            "form": form,
            "next_url": next_url,
        },
    )


def admin_logout(request):
    logout(request)
    messages.success(
        request,
        "You have been logged out.",
    )

    return redirect("school_admin:login")


@admin_required
def admin_dashboard(request):
    User = get_user_model()
    today = timezone.localdate()

    students = Student.objects.filter(is_active=True)
    classes = TeachingClass.objects.filter(is_active=True)
    staff = User.objects.filter(role=User.TEACHER)
    present_today = Attendance.objects.filter(date=today).values(
        "student",
    ).distinct().count()

    class_rows = (
        classes.select_related("staff")
        .annotate(student_count=Count("students"))
        .order_by("name")[:8]
    )
    unassigned_students = students.filter(teaching_class__isnull=True).count()
    recent_assignments = Assignment.objects.select_related(
        "teaching_class",
        "created_by",
    )[:5]

    return render(
        request,
        "admin_portal/dashboard.html",
        {
            "summary": {
                "students": students.count(),
                "classes": classes.count(),
                "staff": staff.filter(is_active=True).count(),
                "present_today": present_today,
                "unassigned_students": unassigned_students,
            },
            "class_rows": class_rows,
            "recent_assignments": recent_assignments,
        },
    )


@admin_required
def admin_staff_list(request):
    User = get_user_model()
    staff = User.objects.filter(role=User.TEACHER).order_by(
        "first_name",
        "last_name",
        "username",
    )

    return render(
        request,
        "admin_portal/staff_list.html",
        {
            "staff": staff,
        },
    )


@admin_required
def admin_staff_create(request):
    form = StaffUserCreateForm()

    if request.method == "POST":
        form = StaffUserCreateForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Staff account {user.username} was created.",
            )
            return redirect("school_admin:staff_list")

    return render(
        request,
        "admin_portal/staff_create.html",
        {
            "form": form,
        },
    )


@admin_required
def admin_class_list(request):
    classes = (
        TeachingClass.objects.select_related("staff")
        .annotate(student_count=Count("students"))
        .order_by("name")
    )

    return render(
        request,
        "admin_portal/class_list.html",
        {
            "classes": classes,
        },
    )


@admin_required
def admin_class_create(request):
    form = TeachingClassAdminForm()

    if request.method == "POST":
        form = TeachingClassAdminForm(request.POST)

        if form.is_valid():
            teaching_class = form.save()
            messages.success(
                request,
                f"{teaching_class.name} was created.",
            )
            return redirect("school_admin:class_list")

    return render(
        request,
        "admin_portal/class_form.html",
        {
            "form": form,
            "title": "Create Class",
            "button_label": "Save Class",
        },
    )


@admin_required
def admin_class_edit(request, class_id):
    teaching_class = get_object_or_404(
        TeachingClass,
        pk=class_id,
    )
    form = TeachingClassAdminForm(instance=teaching_class)

    if request.method == "POST":
        form = TeachingClassAdminForm(
            request.POST,
            instance=teaching_class,
        )

        if form.is_valid():
            teaching_class = form.save()
            messages.success(
                request,
                f"{teaching_class.name} was updated.",
            )
            return redirect("school_admin:class_list")

    return render(
        request,
        "admin_portal/class_form.html",
        {
            "form": form,
            "title": "Edit Class",
            "button_label": "Update Class",
        },
    )


@admin_required
def admin_student_list(request):
    search = request.GET.get("search", "").strip()
    class_id = request.GET.get("class", "").strip()
    students = Student.objects.select_related("teaching_class").order_by(
        "first_name",
        "last_name",
    )

    if search:
        students = students.filter(
            Q(student_id__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(parent_name__icontains=search)
        )

    if class_id:
        students = students.filter(teaching_class_id=class_id)

    classes = TeachingClass.objects.filter(is_active=True).order_by("name")

    return render(
        request,
        "admin_portal/student_list.html",
        {
            "students": students,
            "classes": classes,
            "search": search,
            "class_id": class_id,
        },
    )


@admin_required
def admin_student_assign_class(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related("teaching_class"),
        pk=student_id,
    )
    form = StudentClassAssignmentForm(instance=student)

    if request.method == "POST":
        form = StudentClassAssignmentForm(
            request.POST,
            instance=student,
        )

        if form.is_valid():
            student = form.save()
            StudentParent.objects.filter(student=student).update(
                teaching_class=student.teaching_class,
            )
            messages.success(
                request,
                f"{student.full_name} was assigned successfully.",
            )
            return redirect("school_admin:student_list")

    return render(
        request,
        "admin_portal/student_assign_class.html",
        {
            "form": form,
            "student": student,
        },
    )
