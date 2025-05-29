"""
Definition of models.
"""

from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) 
    can_access_enquiry_form_view= models.BooleanField(default=False)
    can_access_admission_form= models.BooleanField(default=False)
    can_access_all = models.BooleanField(default=False)
    can_access_shortlisted_students_view = models.BooleanField(default=False)
    can_access_shortlist_display = models.BooleanField(default=False)
    can_access_degree_admission_form = models.BooleanField(default=False)
  

 
    def __str__(self):
        return self.username

class ExcelUpload(models.Model):
    file = models.FileField(upload_to='excel_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class StudentRecord(models.Model):
    student_id = models.CharField(max_length=20)
    student_name = models.CharField(max_length=100)
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)
    guardian_relation = models.CharField(max_length=50)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student_name} ({self.student_id})"
class SentMessage(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    send_sms = models.BooleanField(default=False)
    send_whatsapp = models.BooleanField(default=False)
    department = models.CharField(max_length=100)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Add this field for status
    status = models.CharField(max_length=255, default="sms:0 whatsapp:0")

    # Adding foreign keys to link the message to the student and guardian phone
    student_name = models.ForeignKey(StudentRecord, on_delete=models.CASCADE, related_name='sent_messages')
    guardian_phone_no = models.CharField(max_length=15, blank=True, null=True)  # Added phone number field

    def __str__(self):
        return f"{self.subject} ({self.department})"

class MessageDelivery(models.Model):
    message = models.ForeignKey(SentMessage, on_delete=models.CASCADE, related_name='deliveries')
    student = models.ForeignKey(StudentRecord, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20,
        choices=[('Delivered', 'Delivered'), ('Not Delivered', 'Not Delivered'), ('Pending', 'Pending')],
        default='Pending'
    )

    def __str__(self):
        return f"{self.student.student_name} - {self.status}"

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    admission_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, null=True, blank=True)
    parent_phone = models.CharField(max_length=15, null=True, blank=True)
    course_type = models.CharField(max_length=10, choices=[('PU', 'PU'), ('Degree', 'Degree')])
    category = models.CharField(max_length=10, null=True, blank=True)
    quota_type = models.CharField(max_length=20)
    admission_date = models.DateField()

    class Meta:
        db_table = 'master_student'  # tells Django to use your manually created table

    def __str__(self):
        return f"{self.student_name} ({self.admission_no})"

from django.db import models

class Employee (models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    date_joined = models.DateField()
    photo = models.ImageField(upload_to='emp_photos/', null=True, blank=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    semester_number = models.PositiveIntegerField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    subject_code = models.CharField(max_length=20, null=True, blank=True)
    credit = models.PositiveIntegerField(null=True, blank=True)
    faculty = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Sem {self.semester_number}, {self.course.name})"

class Semester(models.Model):
    number = models.PositiveIntegerField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    def __str__(self):
        return f"Sem {self.number} - {self.course.name}"


class CourseType(models.Model):
    id = models.AutoField(primary_key=True)  # AutoIncrement field, UNSIGNED is not explicitly specified in Django
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):
    id = models.AutoField(primary_key=True)  # AutoIncrement field
    name = models.CharField(max_length=100)
    duration_years = models.PositiveIntegerField()  # corresponds to INT UNSIGNED
    total_semesters = models.PositiveIntegerField()  # corresponds to INT UNSIGNED
    course_type = models.ForeignKey(
        CourseType,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    def __str__(self):
        return f"{self.name} ({self.course_type.name})"
