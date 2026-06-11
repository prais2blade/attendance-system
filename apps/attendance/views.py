import json
from json import scanner

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps import attendance
from apps.students.models import Student
from .models import Attendance
from django.db.models import Q
from datetime import timedelta
import csv
from openpyxl import Workbook
from django.http import HttpResponse
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from apps.notifications.attendance_notifications import (
    notify_check_in,
    notify_check_out
)


@method_decorator(csrf_exempt, name="dispatch")
class QRScanView(View):

    def post(self, request):

        try:

            body = json.loads(
                request.body
            )

            student_id = body.get(
                "student_id"
            )

            student = Student.objects.get(
                student_id=student_id
            )

            today = timezone.localdate()

            attendance, created = (
                Attendance.objects.get_or_create(
                    student=student,
                    date=today
                )
            )

            now = timezone.now()

            if attendance.check_in is None:

                attendance.check_in = now

                attendance.save()

                notify_check_in(student)

                return JsonResponse({
                    "status": "CHECK_IN",
                    "student": student.student_id,
                    "time": now.strftime("%H:%M:%S")
                })

            if attendance.check_out is None:

                attendance.check_out = now

                attendance.save()

                notify_check_out(student)

                return JsonResponse({
                    "status": "CHECK_OUT",
                    "student": student.student_id,
                    "time": now.strftime("%H:%M:%S")
                })

            return JsonResponse({
                "status": "ALREADY_COMPLETED"
            })

        except Student.DoesNotExist:

            return JsonResponse({
                "error": "Student not found"
            }, status=404)
            
            

def scanner_view(request):

    return render(
        request,
        "attendance/scanner.html"
    )
    

def dashboard_view(request):

    today = timezone.localdate()

    search = request.GET.get("search", "")

    students = Student.objects.all()
    
    status_filter = request.GET.get(
        "status",
        "all"
    )

    if search:

        students = students.filter(

            Q(student_id__icontains=search) |

            Q(first_name__icontains=search) |

            Q(last_name__icontains=search)

        )

    student_rows = []

    present = 0
    checked_in = 0
    checked_out = 0

    for student in students:

        attendance = Attendance.objects.filter(
            student=student,
            date=today
        ).first()

        status = "ABSENT"

        if attendance:

            present += 1

            if attendance.check_in and not attendance.check_out:

                status = "IN CENTER"
                checked_in += 1

            elif attendance.check_out:

                status = "CHECKED OUT"
                checked_out += 1

        student_rows.append({

            "student": student,
            "attendance": attendance,
            "status": status

        })
        
        if status_filter != "all":

            student_rows = [

                row

                for row in student_rows

                if row["status"] == status_filter

            ]

    total_students = students.count()

    absent = total_students - present

    context = {

        "today": today,

        "student_rows": student_rows,

        "total_students": total_students,

        "present": present,

        "checked_in": checked_in,

        "checked_out": checked_out,

        "absent": absent,

        "search": search,
        
        "status_filter": status_filter,

    }
    
    if request.htmx:

        return render(
            request,
            "attendance/partials/student_table.html",
            {
                "student_rows": student_rows
            }
        )

    return render(
        request,
        "attendance/dashboard_v21.html",
        context
    )
    
def reports_dashboard(request):

    today = timezone.localdate()

    total_students = Student.objects.count()

    present_today = Attendance.objects.filter(
        date=today
    ).count()

    absent_today = (
        total_students - present_today
    )

    attendance_rate = 0

    if total_students > 0:

        attendance_rate = round(
            (present_today / total_students) * 100,
            1
        )

    recent_attendance = Attendance.objects.filter(
        date=today
    ).select_related(
        "student"
    ).order_by(
        "-check_in"
    )[:20]

    context = {

        "today": today,

        "total_students": total_students,

        "present_today": present_today,

        "absent_today": absent_today,

        "attendance_rate": attendance_rate,

        "recent_attendance": recent_attendance

    }

    return render(
        request,
        "attendance/reports_dashboard.html",
        context
    )
    
def reports_dashboard(request):

    today = timezone.localdate()

    report_type = request.GET.get(
        "period",
        "today"
    )
    
    start_input = request.GET.get(
        "start_date"
    )

    end_input = request.GET.get(
        "end_date"
    )

    if report_type == "custom" and start_input and end_input:

        start_date = datetime.strptime(
            start_input,
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            end_input,
            "%Y-%m-%d"
        ).date()

    elif report_type == "yesterday":

        start_date = today - timedelta(days=1)
        end_date = start_date

    elif report_type == "week":

        start_date = today - timedelta(days=6)
        end_date = today

    else:

        start_date = today
        end_date = today

    total_students = Student.objects.count()

    attendance_records = Attendance.objects.filter(

        date__range=[
            start_date,
            end_date
        ]

    )

    present_count = attendance_records.values(
        "student"
    ).distinct().count()

    absent_count = max(
        total_students - present_count,
        0
    )

    attendance_rate = 0

    if total_students:

        attendance_rate = round(

            (
                present_count /
                total_students
            ) * 100,

            1

        )

    recent_attendance = attendance_records.select_related(
        "student"
    ).order_by(
        "-date",
        "-check_in"
    )[:50]

    context = {

        "report_type": report_type,

        "start_date": start_date,

        "end_date": end_date,

        "total_students": total_students,

        "present_today": present_count,

        "absent_today": absent_count,

        "attendance_rate": attendance_rate,

        "recent_attendance": recent_attendance,
        
        "start_input": start_input,
        
        "end_input": end_input,

    }

    return render(
        request,
        "attendance/reports_dashboard.html",
        context
    )
    
def export_attendance_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Student ID",
        "Name",
        "Date",
        "Check In",
        "Check Out"
    ])

    start_date, end_date, _ = get_report_date_range(
    request
)

    records = Attendance.objects.filter(
        date__range=[
            start_date,
            end_date
        ]
    ).select_related(
        "student"
    )

    for record in records:

        writer.writerow([

            record.student.student_id,

            f"{record.student.first_name} "
            f"{record.student.last_name}",

            record.date,

            record.check_in,

            record.check_out

        ])

    return response

def export_attendance_excel(request):

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Attendance"

    headers = [

        "Student ID",
        "Name",
        "Date",
        "Check In",
        "Check Out"

    ]

    sheet.append(headers)

    start_date, end_date, _ = get_report_date_range(
        request
    )

    records = Attendance.objects.filter(
        date__range=[
            start_date,
            end_date
        ]
    ).select_related(
        "student"
    )

    for record in records:

        sheet.append([

            record.student.student_id,

            f"{record.student.first_name} "
            f"{record.student.last_name}",

            str(record.date),

            str(record.check_in),

            str(record.check_out)

        ])

    response = HttpResponse(

        content_type=
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="attendance_report.xlsx"'

    workbook.save(response)

    return response


def get_report_date_range(request):

    today = timezone.localdate()

    report_type = request.GET.get(
        "period",
        "today"
    )

    start_input = request.GET.get(
        "start_date"
    )

    end_input = request.GET.get(
        "end_date"
    )

    if (
        report_type == "custom"
        and start_input
        and end_input
    ):

        start_date = datetime.strptime(
            start_input,
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            end_input,
            "%Y-%m-%d"
        ).date()

    elif report_type == "yesterday":

        start_date = today - timedelta(days=1)
        end_date = start_date

    elif report_type == "week":

        start_date = today - timedelta(days=6)
        end_date = today

    else:

        start_date = today
        end_date = today

    return (
        start_date,
        end_date,
        report_type
    )
    
def export_attendance_pdf(request):

    start_date, end_date, _ = get_report_date_range(
        request
    )

    records = Attendance.objects.filter(
        date__range=[
            start_date,
            end_date
        ]
    ).select_related(
        "student"
    )

    total_students = Student.objects.count()

    present_count = records.values(
        "student"
    ).distinct().count()

    absent_count = max(
        total_students - present_count,
        0
    )

    attendance_rate = 0

    if total_students:

        attendance_rate = round(
            (present_count / total_students) * 100,
            1
        )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="attendance_report.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(

        Paragraph(
            "Attendance Report",
            styles["Title"]
        )

    )

    elements.append(
        Spacer(1, 12)
    )

    elements.append(

        Paragraph(
            f"Period: {start_date} to {end_date}",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Total Students: {total_students}",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Present: {present_count}",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Absent: {absent_count}",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Attendance Rate: {attendance_rate}%",
            styles["Normal"]
        )

    )

    elements.append(
        Spacer(1, 20)
    )

    data = [[

        "Student ID",

        "Name",

        "Date",

        "Check In",

        "Check Out"

    ]]

    for record in records:

        data.append([

            record.student.student_id,

            f"{record.student.first_name} "
            f"{record.student.last_name}",

            str(record.date),

            str(
                record.check_in.strftime(
                    "%H:%M"
                )
            ) if record.check_in else "-",

            str(
                record.check_out.strftime(
                    "%H:%M"
                )
            ) if record.check_out else "-"

        ])

    table = Table(data)

    table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.whitesmoke
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black
            ),

        ])

    )

    elements.append(
        table
    )

    doc.build(elements)

    return response