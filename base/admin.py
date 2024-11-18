from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Teacher, Student, Course, Module, Unit, Material, Quiz, Question, Answer, Result, Complaint
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'user_type', 'is_verified', 'is_staff')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'full_name', 'avatar', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'user_type', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'user_type', 'password1', 'password2'),
        }),
    )# Register your models here.

admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Unit)
admin.site.register(Material)
class AnswerInline(admin.TabularInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Quiz)
admin.site.register(Result)
admin.site.register(Complaint)
