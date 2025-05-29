from django.db import models



# Create your models here.
class Period(models.Model):
    name = models.CharField(max_length=20)  # e.g., "Period 1"
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_extra = models.BooleanField(default=False)
 
    def __str__(self):
        return self.name

# from your_student_app.models import Student
from django.utils import timezone
from master.models import Student,Employee

class PeriodAttendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]
 
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    marked_time = models.DateTimeField(default=timezone.now)
 
    class Meta:
        unique_together = ('student', 'period', 'date')
 
    def __str__(self):
        return f"{self.student.name} - {self.period.name} - {self.date} - {self.status}"