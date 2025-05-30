from django.shortcuts import render, redirect
from .forms import PUAdmissionForm, DegreeAdmissionForm
from .models import PUAdmission, DegreeAdmission


# ---------- PU Admission Form View ----------

def admission_form(request):
    success = False
    next_admission_no = None  # for display in the form

    if request.method == 'POST':
        form = PUAdmissionForm(request.POST, request.FILES)

        if form.is_valid():
            sslc_percentage = form.cleaned_data.get('sslc_percentage')
            quota_type = form.cleaned_data.get('quota_type')
            student_name = form.cleaned_data.get('student_name')

            # Auto-generate admission_no (backend only)
            last_admission = PUAdmission.objects.filter(admission_no__startswith='PU-').order_by('-id').first()
            if last_admission and last_admission.admission_no:
                try:
                    last_number = int(last_admission.admission_no.split('-')[1])
                except (IndexError, ValueError):
                    last_number = 0
            else:
                last_number = 0
            admission_no = f"PU-{last_number + 1:03d}"

            # Fetch enquiry_no by student name
            enquiry_obj = Enquiry.objects.filter(student_name=student_name).first()
            enquiry_no = enquiry_obj.enquiry_no if enquiry_obj else 'None'

            # ATS Screening Logic
            if quota_type == 'Regular':
                application_status = 'Shortlisted' if sslc_percentage >= 60 else 'Rejected'
            elif quota_type == 'Management':
                application_status = 'Shortlisted Management' if sslc_percentage >= 60 else 'Rejected'
            else:
                application_status = 'Pending'

            # Save form data
            pu_admission = form.save(commit=False)
            pu_admission.admission_no = admission_no
            pu_admission.application_status = application_status
            pu_admission.enquiry_no = enquiry_no
            pu_admission.save()

            success = True
            form = PUAdmissionForm()  # reset form

        else:
            print("Form Errors:", form.errors)

    else:
        # Generate next admission number for display
        last_admission = PUAdmission.objects.filter(admission_no__startswith='PU-').order_by('-id').first()
        if last_admission and last_admission.admission_no:
            try:
                last_number = int(last_admission.admission_no.split('-')[1])
            except (IndexError, ValueError):
                last_number = 0
        else:
            last_number = 0
        next_admission_no = f"PU-{last_number + 1:03d}"

        form = PUAdmissionForm()

    return render(request, 'admission/admission_form.html', {
        'form': form,
        'success': success,
        'next_admission_no': next_admission_no,
    })

 
 
# ---------- Degree Admission Form View ----------

def degree_admission_form(request):
    form_submission_success = False
    next_admission_no = None  # for showing in the template

    if request.method == 'POST':
        form = DegreeAdmissionForm(request.POST, request.FILES)
        if form.is_valid():
            pu_percentage = form.cleaned_data.get('pu_percentage')
            quota_type = form.cleaned_data.get('quota_type')
            student_name = form.cleaned_data.get('student_name')

            # Auto-generate admission_no
            last_admission = DegreeAdmission.objects.filter(admission_no__startswith='DG-').order_by('-id').first()
            if last_admission and last_admission.admission_no:
                try:
                    last_number = int(last_admission.admission_no.split('-')[1])
                except (IndexError, ValueError):
                    last_number = 0
            else:
                last_number = 0
            admission_no = f"DG-{last_number + 1:03d}"

            # Fetch enquiry_no
            enquiry_obj = Enquiry.objects.filter(student_name=student_name).first()
            enquiry_no = enquiry_obj.enquiry_no if enquiry_obj else 'None'

            # Screening logic
            if quota_type == 'Regular':
                application_status = 'Shortlisted' if pu_percentage >= 60 else 'Rejected'
            elif quota_type == 'Management':
                application_status = 'Shortlisted Management' if pu_percentage >= 60 else 'Rejected'
            else:
                application_status = 'Pending'

            # Save form
            degree_admission = form.save(commit=False)
            degree_admission.admission_no = admission_no
            degree_admission.application_status = application_status
            degree_admission.enquiry_no = enquiry_no
            degree_admission.save()

            form_submission_success = True
            form = DegreeAdmissionForm()  # reset
        else:
            print("Form Errors:", form.errors)

    else:
        # Generate the next admission_no for display
        last_admission = DegreeAdmission.objects.filter(admission_no__startswith='DG-').order_by('-id').first()
        if last_admission and last_admission.admission_no:
            try:
                last_number = int(last_admission.admission_no.split('-')[1])
            except (IndexError, ValueError):
                last_number = 0
        else:
            last_number = 0
        next_admission_no = f"DG-{last_number + 1:03d}"

        form = DegreeAdmissionForm()

    return render(request, 'admission/degree_admission_form.html', {
        'form': form,
        'form_submission_success': form_submission_success,
        'next_admission_no': next_admission_no,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import PUAdmission, DegreeAdmission, PUAdmissionshortlist, DegreeAdmissionshortlist
import json


def shortlisted_students_view(request):
    stream = request.GET.get('stream', 'PU')

    if stream == 'PU':
        students = PUAdmission.objects.filter(
            Q(application_status__iexact='Shortlisted') |
            Q(application_status__iexact='Shortlisted Management') |
            Q(application_status__iexact='Shortlisted for Management')
        )
        approved_ids = list(
            PUAdmissionshortlist.objects.filter(admin_approved=True).values_list('admission_no', flat=True)
        )
        not_approved_ids = list(
            PUAdmissionshortlist.objects.filter(admin_approved=False).values_list('admission_no', flat=True)
        )

    elif stream == 'Degree':
        students = DegreeAdmission.objects.filter(
            Q(application_status__iexact='Shortlisted') |
            Q(application_status__iexact='Shortlisted Management') |
            Q(application_status__iexact='Shortlisted for Management')
        )
        approved_ids = list(
            DegreeAdmissionshortlist.objects.filter(admin_approved=True).values_list('admission_no', flat=True)
        )
        not_approved_ids = list(
            DegreeAdmissionshortlist.objects.filter(admin_approved=False).values_list('admission_no', flat=True)
        )

    else:
        students = []
        approved_ids = []
        not_approved_ids = []

    context = {
        'stream': stream,
        'students': students,
        'approved_ids': approved_ids,
        'not_approved_ids': not_approved_ids,
    }
    return render(request, 'admission/shortlisted_students.html', context)


@csrf_exempt
def approve_student(request, stream, student_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            approved = bool(int(data.get('approved', 0)))

            if stream == 'PU':
                student = get_object_or_404(PUAdmission, id=student_id)
                shortlist, created = PUAdmissionshortlist.objects.get_or_create(
                    admission_no=student.admission_no,
                    defaults={'quota_type': student.quota_type,
                              'student_name': student.student_name  # Add this
                              }

                )
                shortlist.admin_approved = approved
                shortlist.save()

            elif stream == 'Degree':
                student = get_object_or_404(DegreeAdmission, id=student_id)
                shortlist, created = DegreeAdmissionshortlist.objects.get_or_create(
                    admission_no=student.admission_no,
                    defaults={'quota_type': student.quota_type,
                              'student_name': student.student_name  # Add this
                              }
                )
                shortlist.admin_approved = approved
                shortlist.save()

            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid stream'}, status=400)

            return JsonResponse({'status': 'success', 'approved': shortlist.admin_approved})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# from django.shortcuts import render, redirect
# from .forms import enquiryform
# from .models import enquiry

# from .models import enquiry
# from .forms import enquiryform

# def enquiry_form_view(request):
#     success = false

#     if request.method == 'post':
#         # fetch the latest enquiry again at the time of post
#         last_enquiry = enquiry.objects.order_by('id').last()
#         if last_enquiry and last_enquiry.enquiry_no and last_enquiry.enquiry_no.startswith("enq-"):
#             try:
#                 last_number = int(last_enquiry.enquiry_no.split('-')[1])
#             except (indexerror, valueerror):
#                 last_number = 0
#             next_enquiry_no = f"enq-{last_number + 1:03d}"
#         else:
#             next_enquiry_no = "enq-001"

#         form = enquiryform(request.post)
#         if form.is_valid():
#             enquiry = form.save(commit=false)
#             enquiry.enquiry_no = next_enquiry_no
#             enquiry.save()
#             success = true

#             # now prepare next enquiry no for fresh form
#             next_number = int(next_enquiry_no.split('-')[1]) + 1
#             next_enquiry_no = f"enq-{next_number:03d}"
#             form = enquiryform(initial={'enquiry_no': next_enquiry_no})
#     else:
#         # for get method only
#         last_enquiry = enquiry.objects.order_by('id').last()
#         if last_enquiry and last_enquiry.enquiry_no and last_enquiry.enquiry_no.startswith("enq-"):
#             try:
#                 last_number = int(last_enquiry.enquiry_no.split('-')[1])
#             except (indexerror, valueerror):
#                 last_number = 0
#             next_enquiry_no = f"enq-{last_number + 1:03d}"
#         else:
#             next_enquiry_no = "enq-001"

#         form = enquiryform(initial={'enquiry_no': next_enquiry_no})

#     return render(request, 'admission/enquiry_form.html', {
#         'form': form,
#         'success': success
#     })


from .models import PUAdmissionshortlist, DegreeAdmissionshortlist, PUAdmission, DegreeAdmission

from .models import PUAdmissionshortlist, DegreeAdmissionshortlist
from django.shortcuts import render

def shortlist_display(request):
    selection = request.GET.get('type', 'PU')  # Default to PU
    shortlisted = []

    if selection == 'PU':
        shortlisted = PUAdmissionshortlist.objects.all()
    elif selection == 'Degree':
        shortlisted = DegreeAdmissionshortlist.objects.all()

    return render(request, 'admission/shortlist_display.html', {
        'shortlisted': shortlisted,
        'selection': selection
    })


# views.py
from django.shortcuts import render, get_object_or_404
from .models import PUFeeDetail, PUAdmission, PUAdmissionshortlist
from .forms import PUFeeDetailForm

def pu_fee_detail_form(request, shortlist_id):
    shortlist = get_object_or_404(PUAdmissionshortlist, pk=shortlist_id)
    admission = get_object_or_404(PUAdmission, admission_no=shortlist.admission_no)
    fee = PUFeeDetail.objects.filter(student=admission).first()
    form = PUFeeDetailForm(instance=fee) if fee else PUFeeDetailForm()

    if request.method == 'POST':
        form = PUFeeDetailForm(request.POST, instance=fee)

        if form.is_valid():
            fee_detail = form.save(commit=False)
            fee_detail.student = admission
            fee_detail.admission_no = admission.admission_no  # <--- Auto-fetch and save

            fee_detail.student_name = admission.student_name
            fee_detail.course = admission.category
            fee_detail.final_fee = fee_detail.base_fee - fee_detail.scholarship - fee_detail.advance_amount

            if fee_detail.payment_mode == 'Installment':
                balance = fee_detail.final_fee
                fee_detail.emi_amount = balance / 2 if balance > 0 else 0
            else:
                fee_detail.emi_amount = None
                fee_detail.due_date_1 = None
                fee_detail.due_date_2 = None

            fee_detail.save()

            return render(request, 'admission/fee_detail_form.html', {
                'form': PUFeeDetailForm(instance=fee_detail),
                'fee': fee_detail,
                'success_message': "PU Fee details saved successfully.",
                'admission': admission,
                'type': 'PU',
                'form_title': 'PU Fee Detail Form',
            })


    return render(request, 'admission/fee_detail_form.html', {
        'form': form,
        'admission': admission,
        'type': 'PU',
        'form_title': 'PU Fee Detail Form',
    })


# views.py
from .models import DegreeFeeDetail, DegreeAdmission, DegreeAdmissionshortlist
from .forms import DegreeFeeDetailForm

def degree_fee_detail_form(request, shortlist_id):
    shortlist = get_object_or_404(DegreeAdmissionshortlist, pk=shortlist_id)
    admission = get_object_or_404(DegreeAdmission, admission_no=shortlist.admission_no)

    fee = DegreeFeeDetail.objects.filter(student=admission).first()
    form = DegreeFeeDetailForm(instance=fee) if fee else DegreeFeeDetailForm()

    if request.method == 'POST':
        form = DegreeFeeDetailForm(request.POST, instance=fee)
        if form.is_valid():
            fee_detail = form.save(commit=False)
            fee_detail.student = admission
            fee_detail.admission_no = admission.admission_no  # <--- Auto-fetch and save

            fee_detail.student_name = admission.student_name
            fee_detail.course = admission.category
            fee_detail.final_fee = fee_detail.base_fee - fee_detail.scholarship - fee_detail.advance_amount

            if fee_detail.payment_mode == 'Installment':
                balance = fee_detail.final_fee
                fee_detail.emi_amount = balance / 2 if balance > 0 else 0
            else:
                fee_detail.emi_amount = None
                fee_detail.due_date_1 = None
                fee_detail.due_date_2 = None

            fee_detail.save()

            return render(request, 'admission/fee_detail_form.html', {
                'form': DegreeFeeDetailForm(instance=fee_detail),
                'fee': fee_detail,
                'success_message': "Fee details saved successfully.",
                'admission': admission,
                'type': 'Degree',
                'form_title': 'Degree Fee Detail Form',
            })

    return render(request, 'admission/fee_detail_form.html', {
        'form': form,
        'admission': admission,
        'type': 'Degree',
        'form_title': 'Degree Fee Detail Form',
    })


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import Enquiry1Form
from .models import Enquiry1, Course
from django.contrib import messages

def enquiry1_create(request):
    if request.method == 'POST':
        form = Enquiry1Form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Saved successfully!")
            return redirect('enquiry1_create')
    else:
        # Get the next enquiry_no for display
        last_enquiry = Enquiry1.objects.order_by('-id').first()
        if last_enquiry and last_enquiry.enquiry_no and last_enquiry.enquiry_no.startswith('EQ-'):
            try:
                last_number = int(last_enquiry.enquiry_no.split('-')[1])
            except (IndexError, ValueError):
                last_number = 0
        else:
            last_number = 0
        next_enquiry_no = f"EQ-{last_number+1:02d}"

        form = Enquiry1Form()
    # Pass next_enquiry_no to the template so it can be displayed
    return render(request, 'admission/enquiry1_form.html', {
        'form': form,
        'next_enquiry_no': next_enquiry_no if request.method != 'POST' else None
    })


def load_courses(request):
    course_type_id = request.GET.get('course_type')
    courses = Course.objects.filter(course_type_id=course_type_id).order_by('name')
    return JsonResponse(list(courses.values('id', 'name')), safe=False)


from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import PUAdmissionshortlist, DegreeAdmissionshortlist
from .email_sender import EmailSender

def send_bulk_emails(request):
    if request.method == "POST":
        provider_name = settings.EMAIL_PROVIDER_NAME
        config = settings.EMAIL_PROVIDERS.get(provider_name)
        sender = EmailSender(provider_name, config)

        pu_students = PUAdmissionshortlist.objects.filter(admin_approved=True)
        degree_students = DegreeAdmissionshortlist.objects.filter(admin_approved=True)

        success_count = 0
        for student in list(pu_students) + list(degree_students):
            email = student.email
            if not email:
                continue

            student_name = student.student_name
            username = email.split('@')[0]
            password = 'Temp@1234'

            # Create or update user with default password
            user, created = User.objects.get_or_create(username=username, email=email)
            if created:
                user.set_password(password)
                user.save()

            # ✅ Build the full login URL dynamically
            login_url = request.build_absolute_uri("http://192.168.1.143:8000//admission/student-login/")

            subject = 'Login Credentials for Student Portal'
            html_content = f"""
                <p>Dear {student_name},</p>
                <p>Welcome! Your student account has been created.</p>
                <p><strong>Login URL:</strong> <a href="{login_url}">Login Here</a></p>
                <p><strong>Username:</strong> {username}</p>
                <p><strong>Password:</strong> {password}</p>
                <p>Please change your password after login.</p>
                <p>Regards,<br>Admin</p>
            """

            if sender.send_email(email, subject, html_content):
                success_count += 1

        return HttpResponse(f"✅ {success_count} emails sent successfully.")

    return render(request, 'admission/send_bulk.html')

# yourapp/views.py

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from admission.models import PUAdmissionshortlist, StudentLogin

DEFAULT_PASSWORD = 'Temp@1234'  # Your fixed login password

from django.shortcuts import render, redirect
from .models import StudentLogin
from admission.models import PUAdmissionshortlist, DegreeAdmissionshortlist
from django.contrib import messages

DEFAULT_PASSWORD = "Temp@1234"  # Make sure this constant is defined

def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        shortlist_student = None

        # Step 1: Try fetching from PUAdmissionshortlist
        try:
            shortlist_student = PUAdmissionshortlist.objects.get(student_name=username)
        except PUAdmissionshortlist.DoesNotExist:
            pass

        # Step 2: If not found, try DegreeAdmissionshortlist
        if not shortlist_student:
            try:
                shortlist_student = DegreeAdmissionshortlist.objects.get(student_name=username)
            except DegreeAdmissionshortlist.DoesNotExist:
                messages.error(request, "Invalid student name")
                return render(request, 'admission/student_login.html')

        # Step 3: Check password
        if password != DEFAULT_PASSWORD:
            messages.error(request, "Invalid password")
            return render(request, 'admission/student_login.html')

        # Step 4: Create or get StudentLogin
        student_login, created = StudentLogin.objects.get_or_create(
            admission_no=shortlist_student.admission_no,
            defaults={
                'student_name': shortlist_student.student_name,
                'email': shortlist_student.email,
                # 'phone_number': shortlist_student.parent_mobile_no,
                # 'course': shortlist_student.quota_type,
                'password': DEFAULT_PASSWORD,
            }
        )

        # Step 5: Set session and redirect
        request.session['student_id'] = student_login.id
        return redirect('reset_password')

    return render(request, 'admission/student_login.html')


# @login_required
def reset_password(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = StudentLogin.objects.get(id=student_id)

    if request.method == 'POST':
        new_password = request.POST['new_password']
        student.password = new_password
        student.is_default_password = False
        student.save()
        messages.success(request, "Password changed successfully.")
        return redirect('student_login')

    return render(request, 'admission/reset_password.html', {'student': student})


# fee py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Student
from .forms import StudentForm
from .models import PUFeeDetail, DegreeFeeDetail
from django.utils.timezone import localtime


def student_list(request):
    students = Student.objects.all().prefetch_related('payment_history')
    return render(request, 'admission/student_list.html', {'students': students})



def get_student_details(request):
    admission_no = request.GET.get('admission_no')
    data = {}

    # 🔹 FIRST: Check if data already exists in Student model (latest)
    student = Student.objects.filter(admission_no=admission_no).first()
    if student:
        data = {
            'name': student.name,
            'course': student.course,
            'base_fee': student.base_fee,
            'final_fee': student.final_fee,
        }
    else:
        # 🔹 IF not found in Student, fallback to original PU/Degree detail tables
        pu_student = PUFeeDetail.objects.filter(admission_no=admission_no).first()
        if pu_student:
            data = {
                'name': pu_student.student_name,
                'course': pu_student.course,
                'base_fee': pu_student.base_fee,
                'final_fee': pu_student.final_fee,
            }
        else:
            degree_student = DegreeFeeDetail.objects.filter(admission_no=admission_no).first()
            if degree_student:
                data = {
                    'name': degree_student.student_name,
                    'course': degree_student.course,
                    'base_fee': degree_student.base_fee,
                    'final_fee': degree_student.final_fee,
                }

    return JsonResponse(data)


from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, StudentPaymentHistory
from .forms import StudentForm
from django.utils import timezone

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Student, StudentPaymentHistory
from .forms import StudentForm
from django.utils.timezone import localtime, now

from django.shortcuts import render, redirect
from django.utils.timezone import localtime, now
from .models import Student, StudentPaymentHistory
from .forms import StudentForm

def student_create(request):
    admission_no = request.POST.get('admission_no')
    instance = None

    if admission_no:
        instance = Student.objects.filter(admission_no=admission_no).first()

    form = StudentForm(request.POST or None, instance=instance)

    if form.is_valid():
        student = form.save(commit=False)  # Delay saving to DB

        # Extract fields from form
        amount_paid = form.cleaned_data.get('amount')
        method = form.cleaned_data.get('payment_method')
        final_fee = form.cleaned_data.get('final_fee')
        fee_paid = form.cleaned_data.get('fee_paid')
        next_installment = form.cleaned_data.get('next_installment')
        next_due_date = form.cleaned_data.get('next_due_date')

        current_time = localtime(now())  # Ensures Asia/Kolkata time

        # Assign fee paid datetime to student model
        student.date_of_fee_paid = current_time

        # Save Student model
        student.final_fee = final_fee
        student.save()

        # Create Payment History Entry
        StudentPaymentHistory.objects.create(
            student=student,
            admission_no=student.admission_no,
            name=student.name,
            course=student.course,
            amount=amount_paid,
            base_fee=student.base_fee,
            final_fee=final_fee,
            fee_paid=fee_paid,
            next_installment=next_installment,
            next_due_date=next_due_date,
            date_of_fee_paid=current_time,
            status=student.status,
            payment_method=method
        )

        return redirect('student_list')

    students = Student.objects.all()
    return render(request, 'admission/student_form.html', {'form': form, 'students': students})

def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        return redirect('student_list')
    return render(request, 'admission/student_form.html', {'form': form})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'admission/student_confirm_delete.html', {'student': student})





# views.py
import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.views.decorators.http import require_GET

@require_GET
def generate_qr_dynamic(request):
    amount = request.GET.get("amount")
    if not amount:
        return HttpResponse("Amount is required", status=400)

    upi_id = "9483508971@ybl"  # ✅ Your UPI ID
    upi_link = f"upi://pay?pa={upi_id}&pn=Pinnacle School of Commerce & Management&am={amount}&cu=INR"
    # Optional: add student info as tx note -> &tn=StudentID-123

    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


#receipt

from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Student

def generate_fee_receipt_pdf(request, student_id):
    student = Student.objects.get(id=student_id)
    html_string = render_to_string('admission/student_receipt_pdf.html', {'student': student})
    
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=receipt_{student.student_id}.pdf'
    return response




#fee auto fetch


from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import StudentPaymentHistory

def payment_history(request):
    query = request.GET.get('search')
    
    if query:
        history_list = StudentPaymentHistory.objects.filter(
            Q(admission_no__icontains=query) |
            Q(student__name__icontains=query)
        ).order_by('-id')
    else:
        history_list = StudentPaymentHistory.objects.none()

    paginator = Paginator(history_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'history': page_obj,
        'search_query': query or '',
        'page_obj': page_obj
    }
    return render(request, 'admission/payment_history.html', context)




from .models import Student, StudentPaymentHistory

def save_payment(request):
    if request.method == 'POST':
        admission_no = request.POST.get('admission_no')
        amount_paid = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')

        student = Student.objects.get(admission_no=admission_no)
        student.fee_paid += float(amount_paid)
        student.pending_fee = student.final_fee - student.fee_paid
        student.save()

        StudentPaymentHistory.objects.create(
            student=student,
            admission_no=student.admission_no,
            name=student.name,
            course=student.course,
            amount_paid=amount_paid,
            fee_paid=student.fee_paid,
            pending_fee=student.pending_fee,
            payment_method=payment_method,
        )

        return redirect('student_list')





from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import StudentPaymentHistory

def download_student_receipt(request, pk):
    payment = StudentPaymentHistory.objects.get(pk=pk)
    html_string = render_to_string('admission/student_payment_history_receipt.html', {'payment': payment})
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=student_receipt_{payment.admission_no}.pdf'
    return response

def download_admin_receipt(request, pk):
    payment = StudentPaymentHistory.objects.get(pk=pk)
    html_string = render_to_string('admission/admin_student_payment_history_receipt.html', {'payment': payment})
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=admin_receipt_{payment.admission_no}.pdf'
    return response

from django.http import JsonResponse
from .models import Enquiry1

def enquiry_lookup(request):
    enquiry_no = request.GET.get('enquiry_no')
    form_type = request.GET.get('form_type', '').lower()
    try:
        enquiry = Enquiry1.objects.get(enquiry_no=enquiry_no)
        if form_type in enquiry.course_type.name.lower():
            return JsonResponse({
                "success": True,
                "data": {
                    "student_name": enquiry.student_name,
                    "gender": enquiry.gender,
                    "parent_name": enquiry.parent_name,
                    "parent_mobile_no": enquiry.parent_phone,
                    "address": enquiry.address,
                    "email": enquiry.email,
                    "course_type": enquiry.course_type.id,  # Use .id for <select> fields
                    "course": enquiry.course.id,
                    "sslc_percentage": enquiry.percentage_10th,  # or whatever your field is
                }
            })
        else:
            return JsonResponse({
                "success": False,
                "error": f"Provided enquiry is not for {form_type.upper()} form"
            }, status=404)
    except Enquiry1.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Enquiry number not found"
        }, status=404)

from django.http import JsonResponse
from .models import Enquiry1  # Or your actual enquiry model

from django.http import JsonResponse
from .models import Enquiry1  # Adjust as needed

def degree_enquiry_lookup(request):
    enquiry_no = request.GET.get('enquiry_no')
    try:
        enquiry = Enquiry1.objects.get(enquiry_no=enquiry_no)
        # Check if course_type matches "Degree" (adjust as needed)
        if "degree" in enquiry.course_type.name.lower() or enquiry.course_type.id == 2:  # Adjust logic
            return JsonResponse({
                "data": {
                    "student_name": enquiry.student_name,
                    "gender": enquiry.gender,
                    "parent_name": enquiry.parent_name,
                    "parent_mobile_no": enquiry.parent_phone,
                    "address": enquiry.address,
                    "email": enquiry.email,
                    "course_type": enquiry.course_type.id,  # Use .id for <select> fields
                    "course": enquiry.course.id,
                    "pu_percentage": enquiry.percentage_12th, 
                }
            })
        else:
            return JsonResponse({"error": "Provided enquiry is not for Degree form"}, status=404)
    except Enquiry1.DoesNotExist:
        return JsonResponse({"error": "Enquiry number not found"}, status=404)
