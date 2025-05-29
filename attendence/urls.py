# urls.py
from django.urls import path
from . import views

urlpatterns = [
   
    path('add-period/', views.add_period, name='add_period'),
    path('periods/', views.period_list, name='period_list'),
     path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),

]

