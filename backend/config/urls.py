
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
    "api/attendance/",
    include(
        "apps.attendance.urls"
    )
),
    path("students/", include("apps.students.urls")),
    
    path(
    "api/",
    include(
        "apps.reports.urls"
    )
),
    path(
    "api/",
    include(
        "apps.students.urls"
    )
),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
