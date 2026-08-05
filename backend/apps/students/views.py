import os
import zipfile
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from apps.attendance.models import Attendance

from .admin_auth import admin_required
from .forms import StudentForm, StudentImportForm
from .models import Student, StudentParent
from .services import RegistrationIntegrationService


@admin_required
def student_detail(request, pk):
    student = get_object_or_404(
        Student,
        pk=pk,
    )

    attendance_history = Attendance.objects.filter(student=student).order_by("-date")

    context = {
        "student": student,
        "attendance_history": attendance_history,
    }

    return render(
        request,
        "attendance/detail.html",
        context,
    )


@admin_required
def student_id_card(request, pk):
    student = get_object_or_404(
        Student,
        pk=pk,
    )

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=(85.6 * mm, 54 * mm),
    )

    pdf.setStrokeColor(colors.black)
    pdf.rect(5, 5, 230, 140)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(15, 130, "CODECAMP INNOVATION HUB")

    pdf.setFont("Helvetica", 9)
    pdf.drawString(15, 110, f"Name: {student.first_name} {student.last_name}")
    pdf.drawString(15, 95, f"ID: {student.student_id}")

    if student.qr_code:
        pdf.drawImage(
            student.qr_code.path,
            160,
            40,
            width=60,
            height=60,
        )

    if student.photo:
        pdf.drawImage(
            student.photo.path,
            15,
            40,
            width=50,
            height=50,
        )

    pdf.save()
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"{student.student_id}.pdf",
    )


def parent_portal(request, token):
    student = get_object_or_404(
        Student,
        portal_token=token,
    )

    today = timezone.localdate()

    attendance = Attendance.objects.filter(
        student=student,
        date=today,
    ).first()

    history = Attendance.objects.filter(student=student).order_by("-date")[:30]

    context = {
        "student": student,
        "attendance": attendance,
        "history": history,
    }

    return render(
        request,
        "students/parent_portal.html",
        context,
    )


@admin_required
def import_students(request):
    form = StudentImportForm()

    if request.method == "POST":
        form = StudentImportForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            excel_file = request.FILES["excel_file"]
            workbook = load_workbook(excel_file)
            sheet = workbook.active

            success_count = 0
            failed_count = 0
            errors = []

            for row_number, row in enumerate(
                sheet.iter_rows(
                    min_row=2,
                    values_only=True,
                ),
                start=2,
            ):
                first_name = row[0]
                last_name = row[1]
                date_of_birth = row[2]
                gender = row[3]
                class_name = row[4]
                parent_title = row[5] if len(row) > 5 else ""
                parent_name = row[6] if len(row) > 6 else ""
                parent_email = row[7] if len(row) > 7 else ""
                parent_phone = row[8] if len(row) > 8 else ""
                parent_whatsapp = row[9] if len(row) > 9 else ""
                relationship = row[10] if len(row) > 10 and row[10] else "Guardian"

                if not first_name:
                    continue

                payload = {
                    "first_name": first_name,
                    "last_name": last_name or "",
                    "date_of_birth": date_of_birth,
                    "gender": gender or "",
                    "class_name": class_name or "",
                    "parent_title": parent_title or "",
                    "parent_name": parent_name or "",
                    "parent_email": parent_email or "",
                    "parent_phone": parent_phone or "",
                    "parent_whatsapp": parent_whatsapp or "",
                    "relationship": relationship,
                    "photo": None,
                }

                try:
                    RegistrationIntegrationService.register(payload)
                    success_count += 1
                except Exception as exc:
                    failed_count += 1
                    errors.append(f"Row {row_number}: {exc}")

            if success_count:
                messages.success(
                    request,
                    f"{success_count} student(s) imported successfully.",
                )

            if failed_count:
                messages.warning(
                    request,
                    f"{failed_count} row(s) failed during import.",
                )

                for error in errors[:20]:
                    messages.error(
                        request,
                        error,
                    )

            return redirect("students:student_list")

    context = {
        "form": form,
    }

    return render(
        request,
        "students/import.html",
        context,
    )


@admin_required
def create_student(request):
    form = StudentForm()

    if request.method == "POST":
        form = StudentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            teaching_class = form.cleaned_data.get("teaching_class")

            payload = {
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data.get("last_name", ""),
                "date_of_birth": form.cleaned_data.get("date_of_birth"),
                "gender": form.cleaned_data.get("gender", ""),
                "class_name": (
                    teaching_class.name
                    if teaching_class
                    else form.cleaned_data["class_name"]
                ),
                "teaching_class": teaching_class,
                "parent_title": form.cleaned_data.get("parent_title", ""),
                "parent_name": form.cleaned_data.get("parent_name", ""),
                "parent_email": form.cleaned_data.get("parent_email", ""),
                "parent_phone": form.cleaned_data.get("parent_phone", ""),
                "parent_whatsapp": form.cleaned_data.get("parent_whatsapp", ""),
                "relationship": form.cleaned_data.get("relationship", "Guardian"),
                "photo": request.FILES.get("photo") or form.cleaned_data.get("photo"),
            }

            try:
                result = RegistrationIntegrationService.register(payload)
                student = result["student"]

                if result["parent_created"]:
                    messages.success(
                        request,
                        (
                            "Student registered successfully. "
                            f"Temporary parent password: {result['temporary_password']}"
                        ),
                    )
                else:
                    messages.success(
                        request,
                        f"{student.first_name} registered successfully.",
                    )

                return redirect(
                    "students:student_detail",
                    pk=student.pk,
                )

            except Exception as exc:
                messages.error(
                    request,
                    str(exc),
                )

    context = {
        "form": form,
    }

    return render(
        request,
        "students/create.html",
        context,
    )


@admin_required
def edit_student(request, pk):
    student = get_object_or_404(
        Student,
        pk=pk,
    )

    form = StudentForm(
        instance=student,
    )

    if request.method == "POST":
        form = StudentForm(
            request.POST,
            request.FILES,
            instance=student,
        )

        if form.is_valid():
            student = form.save()

            parent_relation = (
                StudentParent.objects.select_related("parent")
                .filter(student=student)
                .first()
            )

            if parent_relation:
                parent = parent_relation.parent

                parent.title = form.cleaned_data.get(
                    "parent_title",
                    parent.title,
                )
                parent.full_name = form.cleaned_data.get(
                    "parent_name",
                    parent.full_name,
                )
                parent.email = form.cleaned_data.get(
                    "parent_email",
                    parent.email,
                )
                parent.phone_number = form.cleaned_data.get(
                    "parent_phone",
                    parent.phone_number,
                )
                parent.whatsapp_number = form.cleaned_data.get(
                    "parent_whatsapp",
                    parent.whatsapp_number,
                )

                parent.save(
                    update_fields=[
                        "title",
                        "full_name",
                        "email",
                        "phone_number",
                        "whatsapp_number",
                    ]
                )

                relationship = form.cleaned_data.get("relationship")

                if relationship and parent_relation.relationship != relationship:
                    parent_relation.relationship = relationship
                    parent_relation.save(
                        update_fields=[
                            "relationship",
                        ]
                    )

            messages.success(
                request,
                "Student updated successfully.",
            )

            return redirect(
                "students:student_detail",
                pk=student.pk,
            )

    context = {
        "form": form,
        "student": student,
    }

    return render(
        request,
        "students/edit.html",
        context,
    )


@admin_required
def delete_student(request, pk):
    student = get_object_or_404(
        Student,
        pk=pk,
    )

    if request.method == "POST":
        student_name = f"{student.first_name} {student.last_name}"

        student.delete()

        messages.success(
            request,
            f"{student_name} deleted successfully.",
        )

        return redirect("students:student_list")

    context = {
        "student": student,
    }

    return render(
        request,
        "students/delete.html",
        context,
    )


@admin_required
def bulk_qr_download(request):
    if request.method != "POST":
        return redirect("students:student_list")

    student_ids = request.POST.getlist("students")

    if not student_ids:
        messages.warning(
            request,
            "No students were selected.",
        )

        return redirect("students:student_list")

    students = Student.objects.filter(id__in=student_ids).order_by("student_id")

    buffer = BytesIO()

    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for student in students:
            if student.qr_code and os.path.exists(student.qr_code.path):
                archive.write(
                    student.qr_code.path,
                    arcname=f"{student.student_id}.png",
                )

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/zip",
    )
    response["Content-Disposition"] = (
        'attachment; filename="student_qr_codes.zip"'
    )

    return response


@admin_required
def bulk_id_cards(request):
    if request.method != "POST":
        return redirect("students:student_list")

    student_ids = request.POST.getlist("students")

    if not student_ids:
        messages.warning(
            request,
            "No students were selected.",
        )

        return redirect("students:student_list")

    students = Student.objects.filter(id__in=student_ids).order_by("student_id")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    for student in students:
        pdf.setPageSize((85.6 * mm, 54 * mm))
        pdf.setStrokeColor(colors.black)
        pdf.rect(5, 5, 230, 140)

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(15, 130, "CODECAMP INNOVATION HUB")

        pdf.setFont("Helvetica", 9)
        pdf.drawString(15, 110, f"Name: {student.first_name} {student.last_name}")
        pdf.drawString(15, 95, f"ID: {student.student_id}")

        if student.qr_code and os.path.exists(student.qr_code.path):
            pdf.drawImage(
                student.qr_code.path,
                160,
                40,
                width=60,
                height=60,
            )

        if student.photo and os.path.exists(student.photo.path):
            pdf.drawImage(
                student.photo.path,
                15,
                40,
                width=50,
                height=50,
            )

        pdf.showPage()

    pdf.save()
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename="student_id_cards.pdf",
    )


@admin_required
def download_student_template(request):
    file_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "templates",
        "student_import_template.xlsx",
    )

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename="student_import_template.xlsx",
    )


@admin_required
def download_student_template(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Students"

    headers = [
        "first_name",
        "last_name",
        "date_of_birth",
        "gender",
        "class_name",
        "parent_title",
        "parent_name",
        "parent_email",
        "parent_phone",
        "parent_whatsapp",
        "relationship",
    ]

    header_fill = PatternFill(
        start_color="1E40AF",
        end_color="1E40AF",
        fill_type="solid",
    )

    header_font = Font(
        bold=True,
        color="FFFFFF",
    )

    for col_num, header in enumerate(headers, start=1):
        cell = sheet.cell(
            row=1,
            column=col_num,
        )
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font

    sample_row = [
        "John",
        "Doe",
        "2015-04-20",
        "Male",
        "JSS1",
        "Mrs",
        "Jane Doe",
        "jane@example.com",
        "08012345678",
        "08012345678",
        "Mother",
    ]

    for col_num, value in enumerate(sample_row, start=1):
        sheet.cell(
            row=2,
            column=col_num,
        ).value = value

    for column in sheet.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)

        for cell in column:
            value = str(cell.value or "")
            if len(value) > max_length:
                max_length = len(value)

        sheet.column_dimensions[column_letter].width = max_length + 5

    sheet.freeze_panes = "A2"

    instructions = workbook.create_sheet(title="Instructions")

    instructions["A1"] = (
        "CODECAMP ATTENDANCE SYSTEM STUDENT IMPORT TEMPLATE"
    )
    instructions["A1"].font = Font(
        bold=True,
        size=14,
    )

    instructions["A3"] = "Fill one student per row."
    instructions["A4"] = "Do not change the header names."
    instructions["A5"] = "Date format must be YYYY-MM-DD."
    instructions["A6"] = "Gender examples: Male, Female."
    instructions["A7"] = "Relationship examples: Father, Mother, Guardian."
    instructions["A8"] = "Parent email is optional."
    instructions["A9"] = "Parent phone numbers should include leading zero."

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )
    response["Content-Disposition"] = (
        'attachment; filename="student_import_template.xlsx"'
    )

    workbook.save(response)

    return response


@admin_required
def student_list(request):
    search = request.GET.get("search", "").strip()

    students = Student.objects.all().order_by("-id")

    if search:
        students = students.filter(
            Q(student_id__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(parent_name__icontains=search)
        )

    context = {
        "students": students,
        "search": search,
        "total_students": students.count(),
    }

    return render(
        request,
        "students/list.html",
        context,
    )
