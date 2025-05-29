from django.shortcuts import render, redirect
from .forms import PeriodForm
from .models import Period

def period_list(request):
    """
    Display all periods with an option to add a new one via a '+' button.
    """
    periods = Period.objects.all()
    return render(request, 'attendence/period_list.html', {'periods': periods})


from django.shortcuts import render, redirect
from .models import Period
from master.models import Subject


def add_period(request):
    subjects = Subject.objects.all()  # get all subjects for dropdown

    if request.method == 'POST':
        name = request.POST.get('name')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_extra = request.POST.get('is_extra') == 'on'

        # Basic validation (you can expand as needed)
        if name and start_time and end_time:
            period = Period(
                name=name,
                start_time=start_time,
                end_time=end_time,
                is_extra=is_extra
            )
            period.save()
            return redirect('period_list')  # replace with your URL name

    return render(request, 'attendence/add_period.html', {
        'subjects': subjects,
    })







from django.shortcuts import render, redirect
from .models import PeriodAttendance
from .forms import PeriodAttendanceForm

def attendance_list(request):
    records = PeriodAttendance.objects.all().order_by('-date')
    return render(request, 'attendence/attendance_list.html', {'records': records})

def add_attendance(request):
    if request.method == 'POST':
        form = PeriodAttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')
    else:
        form = PeriodAttendanceForm()
    return render(request, 'attendence/add_attendance.html', {'form': form})





