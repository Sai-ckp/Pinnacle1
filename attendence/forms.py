# forms.py
from django import forms
from .models import Period

class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['name', 'start_time', 'end_time', 'is_extra']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'is_extra': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
from django import forms
from .models import PeriodAttendance

class PeriodAttendanceForm(forms.ModelForm):
    class Meta:
        model = PeriodAttendance
        fields = ['student', 'period', 'date', 'status', 'marked_by']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

