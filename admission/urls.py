from django.urls import path
from .views import generate_qr_dynamic
from . import views

urlpatterns = [
    path('admission/form/', views.admission_form, name='admission_form'),
    path('admission/degree/', views.degree_admission_form, name='degree_admission_form'),
     path('shortlisted/', views.shortlisted_students_view, name='shortlisted_students_view'),
    path('approve/<str:stream>/<int:student_id>/', views.approve_student, name='approve_student'),
     # path('enquiry/', views.enquiry_form_view, name='enquiry_form'),
    path('shortlist/', views.shortlist_display, name='shortlist_display'),
    path('pu-fee/<int:shortlist_id>/', views.pu_fee_detail_form, name='pu_fee_detail_form'),
    path('degree-fee/<int:shortlist_id>/', views.degree_fee_detail_form, name='degree_fee_detail_form'),
       path('enquiry1/new/', views.enquiry1_create, name='enquiry1_form'),
    path('enquiry1/create/', views.enquiry1_create, name='enquiry1_create'),
    path('ajax/load-courses/', views.load_courses, name='ajax_load_courses'),

    # path('fee/view/<int:fee_id>/', views.view_fee_detail, name='view_fee_detail'),
       path('admission/send_bulk_emails/', views.send_bulk_emails, name='send_bulk_emails'),

   # path('admission/create-logins/',views. create_student_logins, name='create_student_logins'),

    path('admission/student-login/', views.student_login, name='student_login'),
    path('admissions/reset-password/', views.reset_password, name='reset_password'),

        #Fee
    path('fee/', views.student_list, name='student_list'),
    path('create/', views.student_create, name='student_create'),
    path('update/<int:pk>/', views.student_update, name='student_update'),
    path('delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('get_student_details/', views.get_student_details, name='get_student_details'),
    path("generate-qr-code/", generate_qr_dynamic, name="generate_qr_dynamic"), #QR for Fee
    path('receipt/<int:student_id>/pdf/', views.generate_fee_receipt_pdf, name='generate_fee_receipt_pdf'), # PDF Receipt

    path('save-payment/', views.save_payment, name='save_payment'),

    path('payment-history/', views.payment_history, name='payment_history'),
    path('receipt/student/<int:pk>/', views.download_student_receipt, name='download_student_receipt'),
    path('receipt/admin/<int:pk>/', views.download_admin_receipt, name='download_admin_receipt'),



]
