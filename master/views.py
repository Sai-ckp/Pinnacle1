from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import render, redirect
from .models import User

def blank_view(request):
    return render(request, 'master/blank.html')
 
def custom_login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.password == password:  # plain password check
                request.session['user_id'] = user.id  # simple login session
                
                # Redirect based on user id
                if user.id == 2:
                    return redirect('blank_view')  # change 'special_page' to your URL name
                else:
                    return redirect('dashboard_view')  # redirect after login success
                
            else:
                error = 'Invalid password'
        except User.DoesNotExist:
            error = 'User does not exist'

    users = User.objects.all()  # For user dropdown on login page
    return render(request, 'master/login.html', {'error': error, 'users': users})

@login_required
def dashboard_view(request):
    return render(request, 'master/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm
from .models import ExcelUpload, StudentRecord
import pandas as pd
import os
import pandas as pd
import os
from django.shortcuts import render, redirect
from .models import ExcelUpload, StudentRecord
from .forms import ExcelUploadForm

import pandas as pd
import os
from django.shortcuts import render, redirect
from .models import ExcelUpload, StudentRecord
from .forms import ExcelUploadForm

def student_data_view(request):
    upload_form = ExcelUploadForm()
    files = ExcelUpload.objects.order_by('-uploaded_at')
    table_data = []

    # ✅ Handle file upload
    if request.method == 'POST' and 'upload_submit' in request.POST:
        upload_form = ExcelUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            upload_form.save()
            return redirect('student_data_view')

    # ✅ Combine and read all Excel files
    all_files = ExcelUpload.objects.all()
    combined_df = pd.DataFrame()

    for file_obj in all_files:
        try:
            file_path = file_obj.file.path
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                continue

            # ✅ Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    # ✅ Safe processing
    required_cols = {'student id', 'student name'}

    if not combined_df.empty:
        actual_cols = set(combined_df.columns)
        print("Available columns:", combined_df.columns)

        if required_cols.issubset(actual_cols):
            combined_df.drop_duplicates(subset=['student id', 'student name'], inplace=True)

            existing_records = StudentRecord.objects.values_list('student_id', 'student_name')
            existing_set = set((str(i).strip(), n.strip().lower()) for i, n in existing_records)

            for _, row in combined_df.iterrows():
                student_id = str(row.get('student id', '')).strip()
                student_name = str(row.get('student name', '')).strip().lower()

                if not student_id or not student_name:
                    continue

                if (student_id, student_name) not in existing_set:
                    StudentRecord.objects.create(
                        student_id=student_id,
                        student_name=row.get('student name', ''),
                        guardian_name=row.get('guardian name', ''),
                        guardian_phone=row.get('guardian phone number', ''),
                        guardian_relation=row.get('guardian relation with student', ''),
                        department=row.get('department', '')
                    )
                    existing_set.add((student_id, student_name))
        else:
            print("❌ Required columns missing in Excel. Found only:", actual_cols)

    # ✅ Always show saved data
    saved_records = StudentRecord.objects.all().values(
        'student_id', 'student_name', 'guardian_name',
        'guardian_phone', 'guardian_relation', 'department'
    )
    table_data = list(saved_records)

    return render(request, 'master/student_form.html', {
        'upload_form': upload_form,
        'files': files,
        'table_data': table_data
    })
# from .models import SentMessage, StudentRecord
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.db.models import Q
# from .models import SentMessage, StudentRecord

# @login_required
# def message_history_view(request):
#     # Get filters from URL parameters
#     channel_filter = request.GET.get('channel', '')
#     status_filter = request.GET.get('status', '')
#     department = request.GET.get('department')

#     # Start with all sent messages ordered by 'sent_at' date
#     messages = SentMessage.objects.all().order_by('-sent_at')

#     # Apply channel filters (SMS or WhatsApp)
#     if channel_filter == 'sms':
#         messages = messages.filter(send_sms=True)
#     elif channel_filter == 'whatsapp':
#         messages = messages.filter(send_whatsapp=True)

#     # Apply status and department filters
#     if status_filter:
#         messages = messages.filter(status=status_filter)
#     if department:
#         messages = messages.filter(department=department)

#     # Get the list of departments for the filter dropdown
#     departments = SentMessage.objects.values_list('department', flat=True).distinct()

#     # Process each message and add status and guardian details
#     for msg in messages:
#         # Fetch guardians for the given department of the message
#         students = StudentRecord.objects.filter(department=msg.department)
#         msg.guardians = []

#         # Loop through the guardians to check the status of each one
#         for guardian in students:
#             guardian_status = "Not Delivered"

#             # Check delivery status based on the message channels (SMS/WhatsApp)
#             if msg.send_sms and msg.send_whatsapp:
#                 guardian_status = "Delivered via SMS and WhatsApp"
#             elif msg.send_sms:
#                 guardian_status = "Delivered via SMS"
#             elif msg.send_whatsapp:
#                 guardian_status = "Delivered via WhatsApp"
            
#             # Add the guardian details to the message status
#             msg.guardians.append({
#                 "student": guardian.student_name,
#                 "phone": guardian.guardian_phone,
#                 "status": guardian_status
#             })

#         # Human-readable status based on the message's state
#         if msg.status.lower() == "pending":
#             # If both SMS and WhatsApp failed or are still in progress, mark it as Pending
#             if not msg.send_sms and not msg.send_whatsapp:
#                 msg.status_display = "Not Delivered"
#             else:
#                 msg.status_display = "Pending"
#         else:
#             # If both SMS and WhatsApp were successful, mark it as Delivered
#             if msg.send_sms and msg.send_whatsapp:
#                 msg.status_display = "Delivered"
#             else:
#                 msg.status_display = "Not Delivered"

#     return render(request, 'master/message_history.html', {
#         'messages': messages,
#         'channel_filter': channel_filter,
#         'status_filter': status_filter,
#         'department_filter': department,
#         'departments': departments,
#     })


from django.shortcuts import render
from .models import StudentRecord, SentMessage

def dashboard_view(request):
    total_students = StudentRecord.objects.count()
    messages_sent = SentMessage.objects.count()
    active_departments = SentMessage.objects.values('department').distinct().count()

    # Calculate delivery status counts
    delivered_count = 0
    failed_count = 0

    all_messages = SentMessage.objects.all()
    for msg in all_messages:
        try:
            status_parts = dict(part.split(":") for part in msg.status.split() if ":" in part)
        except ValueError:
            status_parts = {}

        sms_status = status_parts.get("sms", "0")
        whatsapp_status = status_parts.get("whatsapp", "0")

        if sms_status == "1" or whatsapp_status == "1":
            delivered_count += 1
        else:
            failed_count += 1

    delivery_rate = round((delivered_count / messages_sent) * 100, 2) if messages_sent > 0 else 0

    # ✅ Recent 5 messages (delivered or not)
    recent_messages_qs = SentMessage.objects.order_by('-sent_at')[:5]
    recent_messages = []

    for msg in recent_messages_qs:
        try:
            status_parts = dict(part.split(":") for part in msg.status.split() if ":" in part)
        except ValueError:
            status_parts = {}

        sms_status = status_parts.get("sms", "0")
        whatsapp_status = status_parts.get("whatsapp", "0")

        if sms_status == "1" and whatsapp_status == "1":
            msg.status_display = "Delivered via SMS and WhatsApp"
        elif sms_status == "1":
            msg.status_display = "Delivered via SMS"
        elif whatsapp_status == "1":
            msg.status_display = "Delivered via WhatsApp"
        else:
            msg.status_display = "Not Delivered"

        recent_messages.append(msg)

    context = {
        'total_students': total_students,
        'messages_sent': messages_sent,
        'active_departments': active_departments,
        'delivery_rate': delivery_rate,
        'recent_messages': recent_messages,
    }

    return render(request, 'master/dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import StudentRecord, SentMessage
from asgiref.sync import sync_to_async, async_to_sync
import asyncio
from twilio.rest import Client
from django.conf import settings
from functools import partial
from django.utils import timezone

# Async Twilio sender with separate tracking
async def send_twilio_message(to_number, body, send_sms, send_whatsapp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    loop = asyncio.get_event_loop()
    result = {'sms': False, 'whatsapp': False}

    try:
        if send_whatsapp:
            await loop.run_in_executor(
                None,
                partial(
                    client.messages.create,
                    body=body,
                    from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
                    to=f'whatsapp:{to_number}'
                )
            )
            result['whatsapp'] = True
    except Exception as e:
        print(f"❌ WhatsApp failed for {to_number}: {e}")

    try:
        if send_sms:
            await loop.run_in_executor(
                None,
                partial(
                    client.messages.create,
                    body=body,
                    from_=settings.TWILIO_SMS_NUMBER,
                    to=to_number
                )
            )
            result['sms'] = True
    except Exception as e:
        print(f"❌ SMS failed for {to_number}: {e}")

    return result

# ORM helpers wrapped in sync_to_async
@sync_to_async
def get_guardians_queryset(department):
    if department == "All":
        return list(StudentRecord.objects.all())
    return list(StudentRecord.objects.filter(department=department))

@sync_to_async
def create_pending_message(guardian, subject, message_text, send_sms, send_whatsapp):
    status = "sms:0 whatsapp:0"  # Initially not sent
    return SentMessage.objects.create(
        subject=subject,
        message=message_text,
        send_sms=send_sms,
        send_whatsapp=send_whatsapp,
        department=guardian.department,
        status=status,
        student_name=guardian,
        guardian_phone_no=guardian.guardian_phone.strip()
    )

@sync_to_async
def update_message_status(message_obj, status):
    message_obj.status = status
    message_obj.sent_at = timezone.now()
    message_obj.save()

# View Function
def compose_message(request):
    departments = StudentRecord.objects.values_list('department', flat=True).distinct()
    departments = sorted(set(departments))
    selected_department = request.POST.get('department', '')

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        send_sms = 'sms' in request.POST
        send_whatsapp = 'whatsapp' in request.POST
        department = request.POST.get('department')

        async def send_all():
            guardians = await get_guardians_queryset(department)
            full_message = f"Subject: {subject}\n{message_text}"
            failed = 0

            for guardian in guardians:
                phone = guardian.guardian_phone.strip()
                number = f'+91{phone}'  # Update this format if needed

                # Save initial message as pending
                message_obj = await create_pending_message(
                    guardian, subject, message_text, send_sms, send_whatsapp
                )

                # Send messages via Twilio
                result = await send_twilio_message(number, full_message, send_sms, send_whatsapp)

                # Compose actual status string
                status = f"sms:{int(result['sms'])} whatsapp:{int(result['whatsapp'])}"
                await update_message_status(message_obj, status)

                if not result['sms'] and not result['whatsapp']:
                    print(f"❌ Failed to send to: {number}")
                    failed += 1
                else:
                    print(f"✅ Sent to: {number} | Status: {status}")

            return failed

        failed_count = async_to_sync(send_all)()

        if failed_count == 0:
            messages.success(request, "✅ All messages sent successfully.")
        else:
            messages.warning(request, f"⚠️ Sent with {failed_count} failures.")

        return redirect('compose_message')

    return render(request, 'master/compose_message.html', {
        'departments': departments,
        'selected_department': selected_department
    })




# View for Message History with Filter
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SentMessage

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SentMessage


def message_history_view(request):
    channel_filter = request.GET.get('channel', '')
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')

    # Get all messages and apply filters
    messages = SentMessage.objects.all().order_by('-sent_at')

    if channel_filter == 'sms':
        messages = messages.filter(send_sms=True)
    elif channel_filter == 'whatsapp':
        messages = messages.filter(send_whatsapp=True)

    if department_filter:
        messages = messages.filter(department=department_filter)

    departments = SentMessage.objects.values_list('department', flat=True).distinct()

    # Enhance messages with readable status and channel
    filtered_messages = []
    for msg in messages:
        # Safely parse status string like: "sms:1 whatsapp:0"
        status_parts = dict(part.split(":") for part in msg.status.split() if ":" in part)

        sms_status = status_parts.get("sms", "0")
        whatsapp_status = status_parts.get("whatsapp", "0")

        msg.sms_status_display = "Delivered" if sms_status == "1" else "Not Delivered"
        msg.whatsapp_status_display = "Delivered" if whatsapp_status == "1" else "Not Delivered"

        if sms_status == "1" and whatsapp_status == "1":
            msg.status_display = "Delivered via SMS and WhatsApp"
        elif sms_status == "1":
            msg.status_display = "Delivered via SMS"
        elif whatsapp_status == "1":
            msg.status_display = "Delivered via WhatsApp"
        else:
            msg.status_display = "Not Delivered"

        # Sent via channel
        if msg.send_sms and msg.send_whatsapp:
            msg.sent_via = "SMS & WhatsApp"
        elif msg.send_sms:
            msg.sent_via = "SMS"
        elif msg.send_whatsapp:
            msg.sent_via = "WhatsApp"
        else:
            msg.sent_via = "-"

        # Apply status filter logic
        if status_filter == "delivered":
            # At least one is delivered
            if sms_status == "1" or whatsapp_status == "1":
                filtered_messages.append(msg)
        elif status_filter in ["pending", "failed"]:
            # At least one is not delivered
            if sms_status != "1" or whatsapp_status != "1":
                filtered_messages.append(msg)
        elif not status_filter:
            # No filter, include all
            filtered_messages.append(msg)

    return render(request, 'master/message_history.html', {
        'messages': filtered_messages,
        'channel_filter': channel_filter,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'departments': departments,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from twilio.rest import Client
from .models import SentMessage


@login_required
def resend_message_view(request, message_id):
    message = get_object_or_404(SentMessage, id=message_id)

    to_number = f"+91{message.guardian_phone_no.strip()}"
    body = f"Subject: {message.subject}\n{message.message}"

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    result = {'sms': False, 'whatsapp': False}

    try:
        if message.send_whatsapp:
            client.messages.create(
                body=body,
                from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                to=f"whatsapp:{to_number}"
            )
            result['whatsapp'] = True
    except Exception as e:
        print(f"WhatsApp resend failed: {e}")

    try:
        if message.send_sms:
            client.messages.create(
                body=body,
                from_=settings.TWILIO_SMS_NUMBER,
                to=to_number
            )
            result['sms'] = True
    except Exception as e:
        print(f"SMS resend failed: {e}")

    # Update status after resend
    message.status = f"sms:{int(result['sms'])} whatsapp:{int(result['whatsapp'])}"
    message.save()

    messages.success(request, "Message resent successfully.")
    return redirect('compose_message')

from django.shortcuts import render
from admission.models import PUAdmission, PUAdmissionshortlist, DegreeAdmission, DegreeAdmissionshortlist
from master.models import Student
from collections import defaultdict

def student_list(request):
    course_type = request.GET.get('course_type', 'PU')  # Default is PU

    # SYNC APPROVED PU STUDENTS
    pu_shortlisted = PUAdmissionshortlist.objects.filter(admin_approved=True).values_list('admission_no', flat=True)
    pu_students = PUAdmission.objects.filter(admission_no__in=pu_shortlisted)

    for pu in pu_students:
        Student.objects.get_or_create(
            admission_no=pu.admission_no,
            defaults={
                'student_name': pu.student_name,
                'dob': pu.dob,
                'gender': pu.gender,
                'phone': pu.parent_mobile_no,
                'parent_phone': pu.parent_mobile_no,
                'course_type': 'PU',
                'quota_type': pu.quota_type,
                'admission_date': pu.admission_date  # ✅ Add this line
            }
        )

    # SYNC APPROVED DEGREE STUDENTS
    degree_shortlisted = DegreeAdmissionshortlist.objects.filter(admin_approved=True).values_list('admission_no', flat=True)
    degree_students = DegreeAdmission.objects.filter(admission_no__in=degree_shortlisted)

    grouped_by_category = defaultdict(list)
    for deg in degree_students:
        grouped_by_category[deg.category].append(deg)

    for category, students in grouped_by_category.items():
        for deg in students:
            Student.objects.get_or_create(
                admission_no=deg.admission_no,
                defaults={
                    'student_name': deg.student_name,
                    'dob': deg.dob,
                    'gender': deg.gender,
                    'phone': deg.student_phone_no,
                    'parent_phone': deg.parent_phone_no,
                    'course_type': 'Degree',
                    'category': deg.category,
                    'quota_type': deg.quota_type,
                    'admission_date': timezone.now().date()  # fallback default
                }
            )

    # FETCH students after sync
    students = Student.objects.filter(course_type=course_type)

    return render(request, 'master/student_list.html', {
        'students': students,
        'selected_type': course_type
    })



from django.shortcuts import render, redirect
from .models import Employee
from .forms import EmployeeForm

def employee_list_view(request):
    Employees = Employee.objects.all()
    return render(request, 'master/employee_list.html', {'Faculties': Employees})

def employee_add_view(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('master/employee_list')   
    else:
        form = EmployeeForm()
    return render(request, 'master/employee_form.html', {'form': form})




# views.py

from django.shortcuts import render, redirect
from .models import Course, Subject
from .forms import SubjectForm

def subject_list(request):
    subjects = Subject.objects.select_related('course', 'faculty').all()
    return render(request, 'master/subject_list.html', {'subjects': subjects})

from django.shortcuts import render, redirect
from .forms import SubjectForm
from .models import Semester

def add_subject(request):
    semesters = []
    selected_course_id = request.POST.get('course') if request.method == 'POST' else None

    # Fetch semesters only if course is selected (to populate semester dropdown)
    if selected_course_id:
        semesters = Semester.objects.filter(course_id=selected_course_id).order_by('number')

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        semester_number = request.POST.get('semester')  # This is the selected semester number from form

        if form.is_valid() and semester_number:
            subject = form.save(commit=False)
            subject.semester_number = int(semester_number)  # Save semester number as integer
            subject.save()
            return redirect('subject_list')  # Redirect after save
    else:
        form = SubjectForm()

    return render(request, 'master/add_subject.html', {
        'form': form,
        'semesters': semesters,
        'selected_course_id': selected_course_id
    })

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, CourseType
from .forms import CourseForm, CourseTypeForm

# CourseType Views
def course_type_list(request):
    types = CourseType.objects.all()
    return render(request, 'master/course_type_list.html', {'types': types})

def course_type_create(request):
    if request.method == 'POST':
        form = CourseTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_type_list')
    else:
        form = CourseTypeForm()
    return render(request, 'master/course_type_form.html', {'form': form})

# Course Views
def course_list(request):
    courses = Course.objects.select_related('course_type').all()
    return render(request, 'master/course_list.html', {'courses': courses})

def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'master/course_form.html', {'form': form})

def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'master/course_form.html', {'form': form})

def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return redirect('course_list')



from .models import Semester
from .forms import SemesterForm

def semester_list(request):
    semesters = Semester.objects.select_related('course').all()
    return render(request, 'master/semester_list.html', {'semesters': semesters})

def semester_add(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('semester_list')
    else:
        form = SemesterForm()
    return render(request, 'master/semester_form.html', {'form': form})

# views.py
from django.http import JsonResponse
from .models import Course

def get_semester_numbers(request):
    course_id = request.GET.get('course_id')
    try:
        course = Course.objects.get(id=course_id)
        semesters = list(range(1, course.total_semesters + 1))
        return JsonResponse({'numbers': semesters})
    except Course.DoesNotExist:
        return JsonResponse({'numbers': []})










