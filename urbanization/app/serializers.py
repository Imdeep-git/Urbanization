from rest_framework import serializers
from .models import CustomUser, Project, Task, Report

# User Serializer
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'role', 'is_active', 'is_staff')


# Project Serializer with Nested Fields
class ProjectSerializer(serializers.ModelSerializer):
    created_by = CustomUserSerializer(read_only=True)  # Display created_by details
    assigned_to = CustomUserSerializer(read_only=True)  # Display assigned_to details

    class Meta:
        model = Project
        fields = '__all__'


# Task Serializer with Validation and Nested Fields
class TaskSerializer(serializers.ModelSerializer):
    assigned_by = CustomUserSerializer(read_only=True)  # Display assigned_by details
    assigned_to = CustomUserSerializer(read_only=True)  # Display assigned_to details
    project = ProjectSerializer(read_only=True)  # Display project details

    class Meta:
        model = Task
        fields = '__all__'

    # Validate task assignment
    def validate(self, data):
        assigned_to = data.get('assigned_to')
        assigned_by = self.context['request'].user  # Get the user making the request

        # Check that the assigned_to user is not above the role of assigned_by
        if assigned_to and assigned_by.role == 'admin' and assigned_to.role not in ['super_user', 'user']:
            raise serializers.ValidationError("Admins can only assign tasks to Super Users or Users.")
        if assigned_to and assigned_by.role == 'super_user' and assigned_to.role != 'user':
            raise serializers.ValidationError("Super Users can only assign tasks to Users.")

        return data


# Report Serializer with Nested Task and User Details
class ReportSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)  # Display task details
    user = CustomUserSerializer(read_only=True)  # Display user details

    class Meta:
        model = Report
        fields = '__all__'
