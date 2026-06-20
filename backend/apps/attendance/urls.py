from django.urls import path

from .views import QRScanView, dashboard_view, scanner_view, reports_dashboard, export_attendance_csv, export_attendance_excel, export_attendance_pdf

urlpatterns = [
    path(
        "scanner/",
        scanner_view,
        name="scanner"
    ),
    path(
        "scan/",
        QRScanView.as_view(),
        name="scan"
    ),
    path("dashboard/", dashboard_view, name="dashboard"),
    path(
    "reports/",
    reports_dashboard,
    name="reports_dashboard"
),
path(
    "reports/export/csv/",
    export_attendance_csv,
    name="export_attendance_csv"
),

path(
    "reports/export/excel/",
    export_attendance_excel,
    name="export_attendance_excel"
),
path(
    "reports/export/pdf/",
    export_attendance_pdf,
    name="export_attendance_pdf"
),
]