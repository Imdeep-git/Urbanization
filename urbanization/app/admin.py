from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRoles, Project, Task, Report

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if not user.is_authenticated:
            return qs.none()

        if user.is_super_admin:
            return qs
        elif user.is_admin:
            return qs.filter(role__in=[UserRoles.SUPER_USER, UserRoles.USER])
        elif user.is_super_user:
            return qs.filter(role=UserRoles.USER)
        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = request.user

        if not user.is_authenticated:
            return form

        if user.is_super_admin:
            form.base_fields['role'].choices = UserRoles.CHOICES
        elif user.is_admin:
            form.base_fields['role'].choices = [
                (UserRoles.SUPER_USER, 'Super User'),
                (UserRoles.USER, 'User'),
            ]
        elif user.is_super_user:
            form.base_fields['role'].choices = [
                (UserRoles.USER, 'User'),
            ]
        return form

    def has_change_permission(self, request, obj=None):
        user = request.user

        if not user.is_authenticated:
            return False

        if not obj:
            return True
        if user.is_admin and obj.is_super_admin:
            return False
        if user.is_admin and obj.is_admin:
            return False
        if user.is_super_user and obj.role in [UserRoles.SUPER_ADMIN, UserRoles.ADMIN, UserRoles.SUPER_USER]:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        user = request.user
        return user.is_authenticated and (user.is_super_admin or user.is_admin or user.is_super_user)

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

admin.site.register(CustomUser, CustomUserAdmin)

# Project Admin
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'status', 'created_by', 'assigned_to', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('project_name', 'description')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        
        if not user.is_authenticated:
            return qs.none()

        if user.is_super_admin:
            return qs
        elif user.is_admin:
            return qs.filter(created_by=user) | qs.filter(assigned_to=user)
        elif user.is_super_user:
            return qs.filter(assigned_to=user)
        return qs.none()

    def has_module_permission(self, request):
        user = request.user
        return user.is_authenticated and (user.is_super_admin or user.is_admin or user.is_super_user)

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_super_admin:
            return True
        if user.is_admin and obj and obj.created_by == user:
            return True
        if user.is_super_user and obj and obj.assigned_to == user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_super_admin:
            return True
        if user.is_admin and obj and obj.created_by == user:
            return True
        return False

admin.site.register(Project, ProjectAdmin)

# Task Admin
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'status', 'project', 'assigned_by', 'assigned_to', 'due_date', 'completion_date')
    list_filter = ('status', 'due_date', 'completion_date')
    search_fields = ('task_name', 'description')
    ordering = ('-created_at',)

    def has_module_permission(self, request):
        user = request.user
        return user.is_authenticated and (user.is_super_admin or user.is_admin or user.is_super_user)

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

admin.site.register(Task, TaskAdmin)

# Report Admin
class ReportAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('report_details',)
    ordering = ('-created_at',)

    def has_module_permission(self, request):
        user = request.user
        return user.is_authenticated and (user.is_super_admin or user.is_admin or user.is_super_user)

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

admin.site.register(Report, ReportAdmin)
