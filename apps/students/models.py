from django.db import models
import json
import qrcode
from io import BytesIO
from django.core.files import File
import secrets



def generate_student_id():

    last_student = Student.objects.order_by(
        "-id"
    ).first()

    if not last_student:
        return "CDCP-000001"

    last_number = int(
        last_student.student_id.split("-")[1]
    )

    next_number = last_number + 1

    return f"CDCP-{next_number:06d}"

class Student(models.Model):

    student_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    
    gender = models.CharField(
        max_length=10,
        blank=True,
    )
    
    class_name = models.CharField(
        max_length=100,
        blank=True,
    )
    
    parent_name = models.CharField(
        max_length=200,
        blank=True,
    )

    photo = models.ImageField(
        upload_to='students/photos/',
        blank=True,
        null=True
    )

    qr_code = models.ImageField(
        upload_to='students/qrcodes/',
        blank=True,
        null=True
    )
    
    portal_token = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
   
    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def generate_qr_code(self):

        qr_data = {
            "student_id": self.student_id
        }

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5,
        )

        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)

        img = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        buffer = BytesIO()

        img.save(buffer, format="PNG")

        filename = f"{self.student_id}.png"

        self.qr_code.save(
            filename,
            File(buffer),
            save=False
        )
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):

        is_new = self.pk is None
        
        if not self.portal_token:
            self.portal_token = secrets.token_urlsafe(16)

        if not self.student_id:
            self.student_id = generate_student_id()

        super().save(*args, **kwargs)

        if is_new and not self.qr_code:
            self.generate_qr_code()

            super().save(
                update_fields=["qr_code"]
            )
        

class Parent(models.Model):

    TITLE_CHOICES = (

        ("Mr", "Mr"),

        ("Mrs", "Mrs"),

        ("Miss", "Miss"),

        ("Dr", "Dr"),

        ("Pastor", "Pastor"),

        ("Chief", "Chief"),

        ("Alhaji", "Alhaji"),

    )

    title = models.CharField(

        max_length=20,

        choices=TITLE_CHOICES,

        blank=True

    )

    full_name = models.CharField(
        max_length=200
    )

    phone_number = models.CharField(
        max_length=20
    )

    whatsapp_number = models.CharField(
        max_length=20
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    def __str__(self):

        if self.title:

            return f"{self.title} {self.full_name}"

        return self.full_name
    
    
class StudentParent(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="parents"
    )

    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name="students"
    )

    relationship = models.CharField(
        max_length=50,
        default="Guardian"
    )

    def __str__(self):

        return (

            f"{self.student} - "

            f"{self.parent}"

        )