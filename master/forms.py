from django import forms
from .models import Employee, ExcelUpload

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelUpload
        fields = ['file']


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_joined']
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
        }

# forms.py
from django import forms
from .models import Subject

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'course', 'subject_code', 'credit', 'faculty']


from django import forms
from .models import Semester

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['number', 'course']


from django import forms
from .models import Course, CourseType

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'duration_years', 'total_semesters', 'course_type']

class CourseTypeForm(forms.ModelForm):
    class Meta:
        model = CourseType
        fields = ['name']