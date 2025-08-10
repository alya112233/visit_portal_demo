from django.urls import path
from . import views

app_name = 'visits'

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.request_form, name='home'),

    # الواجهة العامة
    path('request/', views.request_form, name='request_form'),
    path('success/', views.request_success, name='request_success'),

    # لوحة الموظف
    path('review/', views.review_list, name='review_list'),
    path('review/<int:pk>/', views.review_detail, name='review_detail'),
    path('review/<int:pk>/approve/', views.approve_request, name='approve_request'),

    # الكرت
    path('ticket/<uuid:token>/', views.ticket_view, name='ticket_view'),
    path('card/<uuid:token>/', views.appointment_card, name='appointment_card'),
]
