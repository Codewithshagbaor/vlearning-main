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

def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'teacher'):
            return view_func(request, *args, **kwargs)
        elif request.user.is_authenticated:
            return render(request, 'error.html', {'message': 'You need to be a teacher to access this page.'})
        else:
            return redirect('teacher_login') # replace with your actual URL for teacher login page
    return wrapper

@teacher_required
def instructor_course_list(request):
    courses = Course.objects.filter(teacher=request.user.teacher)
    return render(request, 'base/instructor/instructor_course_list.html', {'courses': courses})

@teacher_required
def create_course(request):
    
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        course_code = request.POST['course_code']
        course_cover = request.FILES.get('course_cover')

        course = Course.objects.create(
            name=name, 
            description=description,
            course_photo=course_cover,
            course_code=course_code,  # new field
            teacher=request.user.teacher
        )
        messages.success(request, 'Course created successfully.')
        return redirect('dashboard')
    return render(request, 'base/instructor/create_course.html')
@teacher_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user.teacher)
    
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        course_code = request.POST['course_code']
        course_cover = request.FILES.get('course_cover')


        if course_cover:
           course_cover=course_cover
        else:
           course_cover=course.course_photo
          
        course.name = name
        course.description = description
        course.course_code = course_code
        course.course_photo = course_cover
        course.save()
        messages.success(request, 'Course updated successfully.')
        return redirect('dashboard')
    
    return render(request, 'base/instructor/edit_course.html', {'course': course})
@teacher_required
def delete_course(request, course_id):
  course = get_object_or_404(Course, id=course_id, teacher=request.user.teacher)
  if request.method == 'POST':
    course.delete()
    messages.success(request, 'Course deleted successfully.')
    return redirect('teacher_dashboard')

  return render(request, 'base/instructor/delete_course.html', {'course': course})
@teacher_required
def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.prefetch_related('units__materials')
    testlist = Quiz.objects.filter(course_id=course.id)

    context = {
        'course': course,
        'modules': modules,
        'testlist':testlist,
    }
    return render(request, 'base/instructor/course_detail.html', context)

@teacher_required
def manage_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user.teacher)
    students = course.students.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'enroll':
            username = request.POST.get('username')
            try:
                student = User.objects.get(username=username)
                studentrecord = get_object_or_404(Student, form_number=student.student.form_number)
            except User.DoesNotExist:
                messages.error(request, f"Student with email {username} does not exist.")
                return redirect('manage_students', course_id=course_id)

            course.students.add(studentrecord)
            studentrecord.courses.add(course)
            messages.success(request, f"{student.username} enrolled in {course.name} successfully.")

        elif action == 'unenroll':
            student_id = request.POST.get('student_id')
            student = get_object_or_404(Student, form_number=student_id)
            course.students.remove(student)
            student.courses.remove(course)
            messages.success(request, f"{student.first_name} unenrolled from {course.name} successfully.")

        return redirect('manage_students', course_id=course_id)

    context = {
        'course': course,
        'students': students,
    }

    return render(request, 'base/instructor/manage_students.html', context)

@teacher_required
def create_module(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user.teacher)
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        module = Module.objects.create(name=name, description=description, course=course)
        messages.success(request, 'Module created successfully.')
        return redirect('view_course', course_id=course.id)
    return render(request, 'base/instructor/create_module.html', {'course': course})
    
@teacher_required
def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__teacher=request.user.teacher)
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        module.name = name
        module.description = description
        module.save()
        messages.success(request, 'Module updated successfully.')
        return redirect('view_course', course_id=module.course.id)
    return render(request, 'base/instructor/edit_module.html', {'module': module})


@teacher_required
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__teacher=request.user.teacher)
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module deleted successfully.')
        return redirect('edit_course', course_id=module.course.id)
    return render(request, 'base/instructor/delete_module.html', {'module': module})

@teacher_required
def create_unit(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__teacher=request.user.teacher)
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        video_url = request.POST['video_url']
        unit = Unit.objects.create(name=name, description=description, module=module, course=module.course, video_url=video_url)
        messages.success(request, 'Unit created successfully.')
        return redirect('view_course', course_id=module.course.id)
    return render(request, 'base/instructor/create_unit.html', {'module': module})


@teacher_required
def edit_unit(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    if request.method == 'POST':
        unit.name = request.POST['name']
        unit.description = request.POST['description']
        unit.save()
        return redirect('view_course', course_id=unit.module.course.id)
    else:
        return render(request, 'base/instructor/edit_unit.html', {'unit': unit})

@teacher_required
def create_material(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    if request.method == 'POST':
        name = request.POST['name']
        type = request.POST['type']
        file = request.FILES['file']
        material = Material.objects.create(name=name, type=type, file=file, unit=unit, module=unit.module, course=unit.course)
        messages.success(request, 'Material created successfully')
        return redirect('view_course', course_id=unit.course.id)
    return render(request, 'base/instructor/create_material.html', {'unit': unit})


@teacher_required
def edit_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        material.name = request.POST['name']
        material.type = request.POST['type']
        if 'file' in request.FILES:
            material.file = request.FILES['file']
        material.save()
        messages.success(request, 'Material updated successfully')
        return redirect('view_course', course_id=material.course.id)
    return render(request, 'base/instructor/edit_material.html', {'material': material})


@teacher_required
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    unit_id = material.unit.id
    material.delete()
    messages.success(request, 'Material deleted successfully')
    return redirect('view_course', course_id=material.course.id)

@teacher_required
def create_test(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        name = request.POST['name']
        time = request.POST['time']
        required_score_to_pass = request.POST['required_score_to_pass']
        number_of_questions = request.POST['number_of_questions']
        test = Quiz.objects.create(name=name, time=time, required_score_to_pass=required_score_to_pass, number_of_questions=number_of_questions, course=course)
        messages.success(request, 'Test created successfully')
        return redirect('view_course', course_id=course.id,)
    return render(request, 'base/instructor/create_test.html', {'course': course})

@teacher_required
def quiz_view_admin(request, course_id, pk):
    quiz = Quiz.objects.get(pk=pk)
    course = Course.objects.get(id=course_id)
    questions = []

    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.text)
        correct_answer = None
        correct_answers = Answer.objects.filter(question=q, correct=True)
        if correct_answers:
            correct_answer = correct_answers[0].text
        questions.append({
            'question': q.text,
            'link': q.id,
            'answers': answers,
            'correct_answer': correct_answer,
        })

    return render(request, 'base/instructor/quiz_view_questions.html', {'obj':quiz, 'course':course, 'data': questions})

@teacher_required
def create_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        question_text = request.POST.get('question')
        correct_answer_id = request.POST.get('correct_answer')
        if question_text and correct_answer_id:
            question = Question.objects.create(text=question_text, quiz=quiz)
            for i in range(1, 5):
                answer_text = request.POST.get(f'answer_{i}')
                is_correct = (str(i) == correct_answer_id)
                Answer.objects.create(text=answer_text, correct=is_correct, question=question)
            messages.success(request, 'Question has been created successfully.')
            return redirect('quiz_view_admin', course_id=quiz.course.id, pk=quiz.id)
        else:
            messages.error(request, 'Question and Correct Answer fields are required.')
    return render(request, 'base/instructor/create_question.html', {'quiz': quiz})

@teacher_required
def edit_question(request,  quiz_id, question_id):
    question = Question.objects.get(id=question_id)
    answers = Answer.objects.filter(question=question)

    if request.method == 'POST':
        question_text = request.POST.get('question')
        correct_answer_id = request.POST.get('correct_answer')

        if question_text:
            question.text = question_text
            question.save()

        if correct_answer_id:
            for answer in answers:
                answer.correct = (answer.id == int(correct_answer_id))
                answer.save()

        for i in range(1, 5):
            answer_id = request.POST.get(f'answer_{i}_id')
            answer_text = request.POST.get(f'answer_{i}')

            if answer_id:
                answer = Answer.objects.get(id=answer_id)
                answer.text = answer_text
                answer.save()

            else:
                is_correct = (str(i) == correct_answer_id)
                Answer.objects.create(text=answer_text, correct=is_correct, question=question)

        return redirect('quiz_view_admin', pk=quiz_id, course_id=question.quiz.course.id)

    return render(request, 'base/instructor/edit_question.html', {'question': question, 'answers': answers})


@teacher_required
def all_complaints(request):
    complaints = Complaint.objects.all()
    context = {

        'complaints': complaints,
    }
    return render(request, 'base/instructor/view_complaints.html', context)


@teacher_required
def delete_complaints_admin(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.delete()
    messages.success(request, 'Complain deleted successfully')
    return redirect('all_complaints')
@teacher_required
def teacher_student_list(request):
    if not hasattr(request.user, 'teacher'):
        return render(request, 'error.html', {'message': 'You need to be teacher to access this page.'})

    student = Student.objects.all()
    return render(request, 'base/instructor/teacher_student_list.html', {'student': student})