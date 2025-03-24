from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import *
from app.forms import UserForm, ProfileForm
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.models import User
from app.models import Profile
from django.utils.timezone import now
from datetime import datetime, time, timedelta
from django.core.mail import send_mail
from django.http import HttpResponse
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
def home(request):
    return render(request, 'home.html')


# --- REGISTRATION, LOGIN, LOGOUT & PROFILE VIEWS ---
def registration(request):
    uf = UserForm()
    pf = ProfileForm()
    d = {'uf': uf, 'pf': pf}

    if request.method == 'POST' and request.FILES:
        UFD = UserForm(request.POST)
        PFD = ProfileForm(request.POST, request.FILES)

        username = request.POST.get('username')
        email = request.POST.get('email')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'The username "{username}" is already taken. Please log in instead.')
            return redirect('login')

        if User.objects.filter(email=email).exists():
            messages.error(request, f'The email "{email}" is already registered. Please log in instead.')
            return redirect('login')

        if UFD.is_valid() and PFD.is_valid():
            UFO = UFD.save(commit=False)
            password = UFD.cleaned_data['password']
            UFO.set_password(password)
            UFO.save()

            PFO = PFD.save(commit=False)
            PFO.profile_user = UFO
            PFO.save()

            # Send confirmation email
            send_mail(
                'Registration Successful',
                'Thank you for registering! Your registration was successful.',
                'jyotiranjanbanty@gmail.com',
                [UFO.email],
                fail_silently=False
            )

            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
            return redirect('registration')

    return render(request, 'registration.html', d)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('un')
        password = request.POST.get('pw')
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return redirect('login')

    return render(request, 'user_login.html')



@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out Login again to proceed!!!!!")
    
    # Redirect to homepage or login page
    return redirect('index')


# Display Profile
@login_required
def profile_display(request):
    user = request.user
    profile = Profile.objects.get(profile_user=user)
    
    context = {'UO': user, 'PO': profile}
    return render(request, 'profile_display.html', context)

# Change Password
@login_required
def change_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        user = request.user
        user.set_password(password)
        user.save()
        messages.success(request, "Password changed successfully!")
        return redirect('login')
    
    return render(request, 'change_password.html')

# Update Profile
@login_required
def profile_update(request):
    user = request.user
    profile = Profile.objects.get(profile_user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_display')
    
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'UO': user,
        'PO': profile,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'profile_update.html', context)

# Reset Password
@login_required
def reset_password(request):
    if request.method == 'POST':
        username = request.POST['un']
        password = request.POST['pw']

        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successfully!")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found!")
    
    return render(request, 'reset_password.html')


# --- DOCTOR SELECTION VIEWS ---

from django.shortcuts import render, get_object_or_404

@login_required
def get_started(request):
    """
    Displays the list of illnesses fetched from the Doctor table.
    Allows users to select an illness to view doctors with that specialization.
    """
    illnesses = Doctor.objects.values_list('specialization', flat=True).distinct()

    return render(request, 'get_started.html', {
        'illnesses': illnesses
    })


def select_doctors(request):
    """
    Fetches and displays the list of doctors based on the selected illness.
    """
    if request.method == 'POST':
        illness = request.POST.get('illness')  # Get the selected illness from the form
        doctors = Doctor.objects.filter(specialization=illness)

        return render(request, 'select_doctors.html', {
            'doctors': doctors,
            'selected_illness': illness
        })
    else:
        # Handle the case if accessed via GET (direct URL)
        return render(request, 'get_started.html', {
            'error': 'Please select an illness first.'
        })
from django.shortcuts import redirect
from django.urls import reverse

def generate_time_slots(start_time, end_time, interval_minutes):
    """Generate time slots between start and end time in 12-hour format."""
    slots = []
    current_time = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    while current_time < end_datetime:
        # ✅ Display slots in 12-hour format with AM/PM
        slots.append(current_time.strftime('%I:%M %p'))  
        current_time += timedelta(minutes=interval_minutes)

    return slots
def book_appointment(request, doctor_id):
    """View to book an appointment."""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        # Get form data
        patient_name = request.POST.get("patient_name")
        date = request.POST.get("date")
        time_slot = request.POST.get("time_slot")

        # Convert 12-hour format to 24-hour format
        try:
            time_24 = datetime.strptime(time_slot, "%I:%M %p").time()
        except ValueError:
            time_24 = None

        if time_24:
            # Redirect to confirmation page with temporary details
            request.session['temp_appointment'] = {
                'doctor_id': doctor_id,
                'patient_name': patient_name,
                'date': date,
                'time': time_24.strftime('%I:%M %p')
            }
            return redirect('confirm_appointment')

    # GET request: display available slots
    selected_date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    available_slots = get_available_slots(doctor, selected_date)

    return render(request, 'book_appointment.html', {
        'doctor': doctor,
        'available_slots': available_slots,
        'selected_date': selected_date
    })


def get_available_slots(doctor, date):
    """Get all available slots excluding booked ones for a specific doctor and date."""
    # ✅ Generate all slots
    all_slots = generate_time_slots(time(9, 0), time(17, 0), 30)

    # ✅ Fetch booked slots for the selected date
    booked_appointments = Appointment.objects.filter(doctor=doctor, date=date)

    # ✅ Convert booked slots to 12-hour format
    booked_slots = {appointment.time.strftime('%I:%M %p') for appointment in booked_appointments}

    # ✅ Filter only available slots
    available_slots = [slot for slot in all_slots if slot not in booked_slots]

    return available_slots


from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from .models import Doctor, Appointment, Payment
import uuid

def confirm_appointment(request):
    """Confirmation page before finalizing the appointment."""

    temp_appointment = request.session.get('temp_appointment')

    if not temp_appointment:
        return redirect('get_started')

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'confirm':
            doctor = get_object_or_404(Doctor, id=temp_appointment['doctor_id'])

            # ✅ Create the final appointment
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient_name=temp_appointment['patient_name'],
                date=temp_appointment['date'],
                time=datetime.strptime(temp_appointment['time'], "%I:%M %p").time()
            )

            # Clear temp session data
            del request.session['temp_appointment']

            # ✅ Create a payment record
            transaction_id = str(uuid.uuid4())
            Payment.objects.create(
                appointment=appointment,
                transaction_id=transaction_id,
                amount=100,  # Set payment amount
                status='Pending'
            )

            # Redirect to payment page
            return redirect(f'/payment/{transaction_id}/')

        elif action == 'cancel':
            del request.session['temp_appointment']
            return redirect('appointment', doctor_id=temp_appointment['doctor_id'])

    return render(request, 'confirm_cancel.html', {'appointment': temp_appointment})



def confirmation(request):
    """Confirmation page after booking an appointment"""

    # Get the appointment ID from the query string
    appointment_id = request.GET.get('appointment_id')

    if not appointment_id:
        return render(request, 'error.html', {'message': 'Appointment ID missing.'})

    # Fetch the appointment details
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Render the confirmation page with the download button
    return render(request, 'confirmation.html', {'appointment': appointment})




from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from .models import Appointment

def generate_appointment_letter(request, appointment_id):
    """Generate a downloadable PDF appointment letter."""

    # Get the appointment details
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = appointment.doctor

    # Set the PDF filename
    filename = f"Appointment_Letter_{appointment.patient_name}_{appointment.date}.pdf"

    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Set up the PDF document
    doc = SimpleDocTemplate(response, pagesize=LETTER)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.darkblue,
        spaceAfter=20
    )

    content_style = ParagraphStyle(
        "Content",
        parent=styles["Normal"],
        fontSize=12,
        leading=14,
    )

    # PDF content
    content = []

    # Title and Header
    content.append(Paragraph("Appointment Confirmation Letter", title_style))
    content.append(Spacer(1, 12))

    # Patient and Doctor Information Table
    table_data = [
        ["Patient Name:", appointment.patient_name],
        ["Doctor:", f"Dr. {doctor.name}"],
        ["Specialization:", doctor.specialization],
        ["Date:", appointment.date.strftime('%B %d, %Y')],
        ["Time:", appointment.time.strftime('%I:%M %p')]
    ]

    table = Table(table_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    # Additional Information
    content.append(Paragraph("Thank you for booking your appointment with us.", content_style))
    content.append(Paragraph("We look forward to serving you.", content_style))
    content.append(Spacer(1, 30))

    # Contact Information
    content.append(Paragraph("<b>Contact Us:</b>", styles["Heading3"]))
    content.append(Paragraph("Phone: +91-9876543210", content_style))
    content.append(Paragraph("Email: support@yourclinic.com", content_style))
    content.append(Spacer(1, 30))

    # Footer
    content.append(Paragraph("Powered by Online Doctor Consultation System", content_style))

    # Build the PDF
    doc.build(content)

    return response




from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Payment
import json

def payment_page(request, transaction_id):
    """Display the payment page with payment options."""
    payment = get_object_or_404(Payment, transaction_id=transaction_id)

    if request.method == "POST":
        # Simulate payment processing (replace with actual gateway)
        action = request.POST.get('action')

        if action == "pay":
            # ✅ Simulate successful payment (replace with real gateway call)
            payment.status = "Success"
            payment.save()
            return redirect(f'/download-letter/{payment.appointment.id}/')

        elif action == "fail":
            payment.status = "Failed"
            payment.save()
            return redirect(f'/payment-failed/{transaction_id}/')

    return render(request, "payment.html", {"payment": payment})
