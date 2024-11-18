from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . models import Teacher, Student, Course, Module, Unit, Material, Quiz, Question, Answer, Result, Complaint
from django.db.models import Count
from datetime import datetime
import datetime
from django.http import JsonResponse
from django.shortcuts import HttpResponse


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'student'):
            return view_func(request, *args, **kwargs)
        elif request.user.is_authenticated:
            return render(request, 'error.html', {'message': 'You need to be a Student to access this page.'})
        else:
            return redirect('index') # replace with your actual URL for teacher login page
    return wrapper

@student_required
def student_courses(request):
    student = request.user.student
    courses = Course.objects.all()
    enrolled_courses = student.courses.all()
    return render(request, 'base/student/student_courses.html', {'courses': courses, 'enrolled_courses': enrolled_courses})

@student_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student
    student.courses.add(course)
    course.students.add(student)
    messages.success(request, 'You have enrolled in {} successfully.'.format(course.name))
    return redirect('student_courses')

@student_required
def unenroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student
    student.courses.remove(course)
    course.students.remove(student)
    messages.success(request, 'You have unenrolled from {} successfully.'.format(course.name))
    return redirect('student_courses')

@student_required
def user_results(request):
    user = request.user.student
    results = Result.objects.filter(user=user)
    return render(request, 'base/student/user_results.html', {'results': results})

@student_required
def all_complaints_student(request):
    user = request.user.student
    complaints = Complaint.objects.filter(student=user)
    context = {

        'complaints': complaints,
    }
    return render(request, 'student_templates/view_complaints.html', context)

@student_required
def submit_complaint(request):
    
    student = request.user.student

    if request.method == 'POST':
        # Process the submitted complaint
        course = get_object_or_404(Course, name=request.POST.get('course'))
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        Complaint.objects.create(course=course, student=student, subject=subject, message=message)
        messages.info(request, 'Complain submitted')
        return redirect('dashboard')

    return render(request, 'student_templates/submit_complaint.html', {'course': course})

@student_required
def delete_complaints(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.delete()
    messages.success(request, 'Complain deleted successfully')
    return redirect('all_complaints_student')

def study(request, course_id):
    time = datetime.datetime.now()
    # Get the selected course object
    course = get_object_or_404(Course, pk=course_id)

    # Get all the modules for the selected course
    modules = course.modules.all()

    # Get the first module of the course
    first_module = modules.first()

    # If no module exists for the course, set first module to None
    if not first_module:
        first_module = None

    # Get the units for the first module
    units = first_module.units.all() if first_module else None

    # Get the first unit of the first module
    first_unit = units.first() if units else None

    # If no unit exists for the first module, set first unit to None
    if not first_unit:
        first_unit = None

    # If a unit is selected, get the video URL for that unit
    unit_video_url = None
    if request.GET.get('unit'):
        unit_id = request.GET.get('unit')
        unit = get_object_or_404(Unit, pk=unit_id)
        unit_video_url = unit.video_url

    # Render the study template with the course, modules, units, and first unit
    return render(request, 'base/student/study.html', {
        'course': course,
        'modules': modules,
        'units': units,
        'selected_unit': request.GET.get('unit'),
        'first_unit': first_unit,
        'unit_video_url': unit_video_url,
        'time': time,
    })

def quiz_view(request, course_id, pk):
  quiz = Quiz.objects.get(pk=pk)
  course = Course.objects.get(id=course_id)
  if Result.objects.filter(user=request.user.student, quiz=quiz).exists():
    return redirect('dashboard')
  else:
    quiz = Quiz.objects.get(pk=pk)
  return render(request, 'base/student/Quiz/quiz.html', {'obj':quiz})

def quiz_data_view(request, course_id, pk):
  quiz = Quiz.objects.get(pk=pk)
  course = Course.objects.get(id=course_id)
  questions = []

  for q in quiz.get_questions():
    answers = []
    for a in q.get_answers():
      answers.append(a.text)
    questions.append({str(q): answers})
  return JsonResponse({
    'data': questions,
    'time': quiz.time,
  })

def save_quiz_view(request, course_id, pk):
  if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
    questions = []
    data = request.POST
    data_ = dict(data.lists())
    data_.pop('csrfmiddlewaretoken')
    for k in data_.keys():
      print('key: ', k)
      question = Question.objects.get(text=k)
      questions.append(question)
    print(questions)

    user = request.user.student
    course = Course.objects.get(id=course_id)
    quiz = Quiz.objects.get(pk=pk)

    score = 0
    multiplier = 100 / quiz.number_of_questions
    results = []

    correct_answer = None
    for q in questions:
      a_selected = request.POST.get(q.text)

      if a_selected != "":
        question_answers = Answer.objects.filter(question=q)
        for a in question_answers:
          if a_selected == a.text:
            if a.correct:
              score += 1
              correct_answer = a.text
          else:
            if a.correct:
              correct_answer = a.text
        results.append({str(q): {'correct_answer':correct_answer, 'answered': a_selected}})
      else:
        results.append({str(q): 'not answered'})
    
    score_ = score * multiplier
    Result.objects.create(quiz=quiz, user=user, course=course, score=score_)

    if score_ >= quiz.required_score_to_pass:
      return JsonResponse({'passed': True, 'score':score_, 'results': results})
    else:
      return JsonResponse({'passed': False, 'score':score_, 'results': results})

#Logout Rules
