from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Define User Roles
class UserRoles:
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    SUPER_USER = 'super_user'
    USER = 'user'

    CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (ADMIN, 'Admin'),
        (SUPER_USER, 'Super User'),
        (USER, 'User'),
    ]


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role=UserRoles.USER, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', UserRoles.SUPER_ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password=password, **extra_fields)


# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRoles.CHOICES, default=UserRoles.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def is_super_admin(self):
        return self.role == UserRoles.SUPER_ADMIN

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN

    @property
    def is_super_user(self):
        return self.role == UserRoles.SUPER_USER

    @property
    def is_standard_user(self):
        return self.role == UserRoles.USER


# Project Model
class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    project_name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(CustomUser, related_name='projects_created', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUser, related_name='projects_assigned', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField()
    project_file = models.FileField(upload_to='projects/files/', null=True, blank=True)  # File input field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name


# Task Model
class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    task_name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(CustomUser, related_name='tasks_assigned', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUser, related_name='tasks_received', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    task_file = models.FileField(upload_to='tasks/files/', null=True, blank=True)  # File input field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name


# Report Model
class Report(models.Model):
    STATUS_CHOICES = [
        ('reviewed', 'Reviewed'),
        ('not_reviewed', 'Not Reviewed'),
    ]

    task = models.ForeignKey(Task, related_name='reports', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='reports', on_delete=models.CASCADE)
    report_details = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_reviewed')
    report_file = models.FileField(upload_to='reports/files/', null=True, blank=True)  # File input field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report for Task {self.task.id} by User {self.user.email}"
