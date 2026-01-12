from django.db import models
from django.contrib.auth.models import AbstractUser



# Models

class User(AbstractUser):
    Roles = (
            ('admin', 'Admin'),
            ('teacher', 'Teacher'),
)
    role = models.CharField(max_length=10, choices=Roles, default= 'admin')
    address = models.TextField(max_length=20, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    profile_pic = models.ImageField(upload_to= 'profile_pics/', blank=True, null=True)


    def __str__(self):                                     return f"{self.username} ({self.user_type})"

#class for Teachers
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(max_length=20, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    subject = models.TextField(max_length=100, blank=False, null=False)




    def __str__(self):
        return self.user.username
