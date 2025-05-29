from django import forms
from .models import PUAdmission

from django import forms
from .models import PUAdmission

from django import forms
from .models import PUAdmission

class PUAdmissionForm(forms.ModelForm):
    class Meta:
        model = PUAdmission
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'admission_no': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }


from django import forms
from .models import DegreeAdmission

from django import forms
from .models import DegreeAdmission

class DegreeAdmissionForm(forms.ModelForm):
    class Meta:
        model = DegreeAdmission
        fields = [
            'enquiry_no',
            'admission_no',
            'student_name',
            'gender',
            'caste',
            'student_phone_no',
            'parent_phone_no',
            'pu_percentage',
            'pu_reg_no',
            'year_of_passing',
            'dob',
            'photo',
            'course_type',
            'course',
            'quota_type',
            'application_status',
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'admission_no': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

from django import forms
from .models import Enquiry1, Course, CourseType

class Enquiry1Form(forms.ModelForm):
    class Meta:
        model = Enquiry1
        fields = [
            'enquiry_no', 'student_name', 'gender', 'parent_relation', 'parent_name', 'parent_phone',
            'course_type', 'course', 'percentage_10th', 'percentage_12th', 'address', 'email'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically filter courses by course_type if present in form data
        if 'course_type' in self.data:
            try:
                course_type_id = int(self.data.get('course_type'))
                self.fields['course'].queryset = Course.objects.filter(course_type_id=course_type_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['course'].queryset = Course.objects.none()
        elif self.instance.pk and self.instance.course_type:
            self.fields['course'].queryset = Course.objects.filter(course_type=self.instance.course_type).order_by('name')
        else:
            self.fields['course'].queryset = Course.objects.none()



from django import forms
from .models import PUFeeDetail,DegreeFeeDetail

class PUFeeDetailForm(forms.ModelForm):
    class Meta:
        model = PUFeeDetail
        exclude = ['student', 'final_fee', 'emi_amount', 'created_at']
        widgets = {
            'due_date_1': forms.DateInput(attrs={'type': 'date'}),
            'due_date_2': forms.DateInput(attrs={'type': 'date'}),
        }

class DegreeFeeDetailForm(forms.ModelForm):
    class Meta:
        model = DegreeFeeDetail
        exclude = ['student', 'final_fee', 'emi_amount', 'created_at']
        widgets = {
            'due_date_1': forms.DateInput(attrs={'type': 'date'}),
            'due_date_2': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms
from .models import StudentLogin

class StudentLoginForm(forms.ModelForm):
    class Meta:
        model = StudentLogin
        fields = ['admission_no', 'password']  # user enters only these


from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['date_of_fee_paid']
        fields = '__all__'
        widgets = {
            'next_due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Keep only 'Cash' and 'Online' in payment_method
        self.fields['payment_method'].choices = [
            choice for choice in self.fields['payment_method'].choices
            if choice[0] in ['Cash', 'Online']
        ]

        # Force 'status' field to only show "Paid"
        self.fields['status'].choices = [('Paid', 'Paid')]
        self.fields['status'].initial = 'Paid'  # optional: set default selected

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = 'Paid'  # always save as Paid
        if commit:
            instance.save()
        return instance

