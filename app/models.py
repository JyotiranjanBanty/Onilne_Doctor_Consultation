from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
class Profile(models.Model):
    profile_user=models.OneToOneField(User,on_delete=models.CASCADE)
    address=models.TextField()
    profile_pic=models.ImageField(upload_to='abcd')
    def __str__(self):
        return self.profile_user.username
    


# models.py
from django.db import models

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)  # Related to illness
    experience = models.IntegerField()  # Years of experience
    mobile_number = models.CharField(max_length=15)
    rating = models.FloatField()  # Rating out of 5
    

    def __str__(self):
        return self.name
    


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.patient_name} with {self.doctor.name} on {self.date} at {self.time}"
    


from django.db import models

class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=(
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed')
    ))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"




