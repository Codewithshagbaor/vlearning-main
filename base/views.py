from django.shortcuts import render, redirect
# import the authentication modules
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import User
from django.contrib.auth.decorators import login_required
import random
from django.db.models import Avg
from django.core.paginator import Paginator
from . models import Teacher, Student, Course, Module, Unit, Material, Quiz, Question, Answer, Result, Complaint
from .utils import query_claude

User = get_user_model()
def render_toast(type, message):
    toast_base = (
        '<div id="dismiss-toast" class="hs-removing:translate-y-5 hs-removing:opacity-0 transition duration-300 max-w-xs bg-white border border-gray-200 z-0 rounded-xl w-full shadow-lg dark:bg-neutral-800 dark:border-neutral-700" role="alert" tabindex="-1" aria-labelledby="hs-toast-dismiss-button-label">'
        '<div class="flex justify-between p-4">'
        '<div class="flex w-full">'
        '{icon}'
        '<div class="ms-3">'
        '<p id="hs-toast-{type}-example-label" class="text-sm text-gray-700 dark:text-neutral-400">{message}</p>'
        '</div>'
        '</div>'
        '<button type="button" class="ms-auto inline-flex justify-center items-center size-5 rounded-lg text-gray-800 opacity-50 hover:opacity-100 focus:outline-none focus:opacity-100 dark:text-white" aria-label="Close" data-hs-remove-element="#dismiss-toast">'
        '<span class="sr-only">Close</span>'
        '<svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M18 6 6 18"></path><path d="m6 6 12 12"></path>'
        '</svg>'
        '</button>'
        '</div>'
        '</div>'
    )

    icons = {
        "success": '<svg class="shrink-0 size-4 text-teal-500 mt-0.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"></path></svg>',
        "error": '<svg class="shrink-0 size-4 text-red-500 mt-0.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path></svg>',
    }

    return toast_base.format(type=type, message=message, icon=icons[type])

def index(request):
    return render(request, 'base/index.html')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'base/auth/auth_login.html')
@login_required
def dashboard(request):
    user_role = request.user.user_type  # Assume `role` is a field in the User model
    user_role = user_role.lower()
    # Default context
    context = {
        "user": request.user,
        "title": "Dashboard",
    }

    # Role-specific templates and context data
    if user_role == 'student':
        template = 'base/student/dashboard.html'
        student = Student.objects.get(user=request.user)
        courses = student.enrolled_courses.all()
        course_tests = []
        course_materials = []
        for course in courses:
            tests = course.tests.all()
            course_tests.append((course, tests))
            materials = course.materials.all()
            course_materials.append((course, materials))
        context.update({
            'courses': courses,
            'course_tests': course_tests,
            'course_materials': course_materials,
            'student': student,
        })
    elif user_role == 'instructor':
        template = 'base/instructor/dashboard.html'
        courses = Course.objects.filter(teacher=request.user.teacher)
        course_count = courses.count()
        module_count = Module.objects.filter(course__in=courses).count()
        unit_count = Unit.objects.filter(course__in=courses).count()
        material_count = Material.objects.filter(course__in=courses).count()
        test_count = Quiz.objects.filter(course__in=courses).count()
        student_count = Student.objects.filter(enrolled_courses__in=courses).distinct().count()

        course_pie_data = []

        for course in courses:
            course_pie_data.append({'name': course.name, 'y': course.students.count()})
        context.update({
            'courses': courses,
            'course_count': course_count,
            'module_count': module_count,
            'unit_count': unit_count,
            'material_count': material_count,
            'test_count': test_count,
            'student_count': student_count,
            'course_pie_data': course_pie_data,
        })
    elif user_role == 'admin':
        template = 'base/admin/admin_dashboard.html'
        context.update({
            "site_stats": "Admin site statistics",
            "user_management": "User management tools",
            # Add other admin-specific context here
        })
    else:
        template = 'base/error.html'
        context.update({
            "error_message": "Unrecognized role",
        })

    return render(request, template, context)
def login_handler(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(render_toast('success', 'Login successful!<script>setTimeout(function () { window.location.href="/dashboard/";}, 2000);</script>'))
        else:
            return render(request, 'core/auth_login.html')
    return render(request, 'core/auth_login.html')

def logout_handler(request):
    logout(request)

    return redirect('/')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course
from .utils import query_claude

@login_required
def ai_chat_view(request):
    chat_history = request.session.get("chat_history", [])
    course_recommendation = None
    question_count = sum(1 for msg in chat_history if msg["type"] == "User")

    if request.method == 'POST':
        user_input = request.POST.get("user_input")
        chat_history.append({"type": "User", "message": user_input})

        # Send user input to Claude to get a follow-up question or recommendation
        if question_count < 1:
            ai_response = query_claude("Continue the conversation to find the best course for the user", [msg["message"] for msg in chat_history])
            chat_history.append({"type": "AI", "message": ai_response})
        else:
            # Query the database to suggest a course
            suggested_course = Course.objects.first()  # Use logic here to select a relevant course
            course_recommendation = suggested_course

        # Save chat history in session
        request.session["chat_history"] = chat_history
    # delete chat history after 2 questions
    if question_count >= 2:
        del request.session["chat_history"]
    return render(request, 'ai_chat.html', {
        'chat_history': chat_history,
        'course_recommendation': course_recommendation,
        'question_count': question_count
    })
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib import messages

User = get_user_model()

@transaction.atomic
def register_student(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        profile_pic = request.FILES.get('profile_pic')

        # Check if email or username already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register_student')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already in use.")
            return redirect('register_student')

        # Create the user and student objects
        user = User.objects.create(
            email=email,
            username=username,
            user_type='STUDENT',
            full_name=f"{first_name} {last_name}",
            password=make_password(password)
        )

        student = Student.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            profile_pic=profile_pic
        )

        messages.success(request, "Registration successful! Please sign in.")
        return redirect('login')

    return render(request, 'base/auth/register.html')