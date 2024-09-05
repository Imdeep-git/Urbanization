from rest_framework import viewsets, permissions
from .models import CustomUser, Project, Task, Report
from .serializers import CustomUserSerializer, ProjectSerializer, TaskSerializer, ReportSerializer

# User ViewSet
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]


# Project ViewSet
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Super Admin can view all projects
        if user.is_super_admin:
            return Project.objects.all()
        # Admins can view projects they created or assigned to them
        elif user.is_admin:
            return Project.objects.filter(created_by=user) | Project.objects.filter(assigned_to=user)
        # Super Users and Users see only projects assigned to them
        return Project.objects.filter(assigned_to=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# Task ViewSet
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Super Admin can view all tasks
        if user.is_super_admin:
            return Task.objects.all()
        # Admins and Super Users can view tasks they assigned or received
        elif user.is_admin or user.is_super_user:
            return Task.objects.filter(assigned_by=user) | Task.objects.filter(assigned_to=user)
        # Users see only tasks assigned to them
        return Task.objects.filter(assigned_to=user)

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


# Report ViewSet
class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Super Admin can view all reports
        if user.is_super_admin:
            return Report.objects.all()
        # Admins, Super Users, and Users can see reports they submitted
        return Report.objects.filter(user=user)
