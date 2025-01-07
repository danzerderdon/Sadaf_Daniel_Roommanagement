
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
# Create your models here.


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class UserAccount(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('planner', 'Planner')
    ]


    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='viewer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for admin access

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return True

    def is_viewer(self):
        """Check if the user is a viewer."""
        return self.role == 'viewer'

    def is_planner(self):
        """Check if the user is a planner."""
        return self.role == 'planner'


class Building(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    floor_count = models.IntegerField()

class Room(models.Model):
    number = models.CharField(max_length=50)
    capacity = models.IntegerField()
    equipment = models.TextField()
    building = models.ForeignKey(Building, on_delete=models.CASCADE)

class RoomBooking(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

class UserCalendar(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    event_description = models.TextField()
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

class RoomCategory(models.Model):
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=100)
