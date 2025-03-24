"""
URL configuration for project101 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',home,name='index'),
    path('registration/',registration,name='registration'),
    path('login/',user_login, name='login'),
    path('logout/',user_logout, name='logout'),
    path('get_started/',get_started,name='get_started'),
    path('select_doctors/',select_doctors, name='select_doctors'), # Correct pattern
    path('reset_password/',reset_password, name='reset_password'), # Correct pattern
    path('profile_display/',profile_display, name='profile_display'),        # Correct pattern
    path('profile_update/',profile_update, name='profile_update'),  # Correct pattern       
    path('change_password/',change_password, name='change_password'), # Correct pattern
    path('appointment/<int:doctor_id>/',book_appointment, name='appointment'), # Correct pattern
    path('confirmation/',confirmation, name='confirmation'), # Correct pattern
    path('generate_pdf/<int:appointment_id>/',generate_appointment_letter, name='generate_pdf'),
    path('confirm_appointment/',confirm_appointment, name='confirm_appointment'),
    path('payment/<str:transaction_id>/', payment_page, name='payment_page'),
    path('payment-failed/<str:transaction_id>/',payment_page, name='payment_failed'),
]
