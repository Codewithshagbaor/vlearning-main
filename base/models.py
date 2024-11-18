from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
# Create your models here.
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('STUDENT', 'Student'),
        ('INSTRUCTOR', 'Instructor'),
        ('ADMIN', 'Admin'),
    )

    user_type = models.CharField( 
        max_length = 20, 
        choices = USER_TYPE_CHOICES, 
        default = '1'
    )
    email = models.EmailField(_('email address'),unique=True)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    avatar = models.ImageField(upload_to='UserAvatar', default="UserAvatar/1.jpg")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_(
        'Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.'
        ),
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type', 'full_name']

    def __str__(self):
        return self.username
    
import random


class Teacher(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
  bio = models.TextField(max_length=500, blank=True)
  profile_pic = models.ImageField(upload_to='teacher_profile_pics', blank=True)

  def __str__(self):
    return self.user.username


class Student(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    courses = models.ManyToManyField('Course', related_name='enrolled_students', blank=True)
    profile_pic = models.ImageField(upload_to='student_profile_pics', blank=True)


    def __str__(self):
        return self.user.username


class Course(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='courses_taught')
    students = models.ManyToManyField(Student, related_name='enrolled_courses')
    course_code = models.CharField(max_length=10)

    course_photo = models.ImageField(upload_to='course_cover_photo', blank=True)

    def __str__(self):
        return self.name

class Module(models.Model):
  name = models.CharField(max_length=255)
  description = models.TextField()
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    
    
class Unit(models.Model):
  name = models.CharField(max_length=255)
  description = models.TextField()
  module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='units')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
  video_url = models.URLField()

    
    
class Material(models.Model):
  VIDEO = 'video'
  DOCUMENT = 'document'
  PICTURE = 'picture'
  ASSIGNMENT = 'assignment'
  MATERIAL_CHOICES = [
        (VIDEO, 'Video'),
        (DOCUMENT, 'Document'),
        (PICTURE, 'Picture'),
        (ASSIGNMENT, 'Assignment'),
  ]
  name = models.CharField(max_length=255)
  type = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
  file = models.FileField(upload_to='materials/%Y/%m/%d/')
  unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='materials')
  module = models.ForeignKey(Module, on_delete=models.CASCADE,related_name='materials')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')


class Quiz(models.Model):
    name = models.CharField(max_length=120)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tests')
    number_of_questions = models.IntegerField()
    time = models.IntegerField(help_text="duration of the quiz in minutes")
    required_score_to_pass = models.IntegerField(help_text="required score in %")

    def __str__(self):
        return f"{self.name}-{self.course}"

    def get_questions(self):
        questions = list(self.question_set.all())
        random.shuffle(questions)
        return questions[:self.number_of_questions]

    class Meta:
        verbose_name_plural = 'Quizes'

class Question(models.Model):
    text = models.CharField(max_length=200)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.text)

    def get_answers(self):
        return self.answer_set.all()

class Answer(models.Model):
    text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"question: {self.question.text}, answer: {self.text}, correct: {self.correct}"


class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='test_results')
    user =  models.ForeignKey(Student, on_delete=models.CASCADE, related_name='test_results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='test_results')
    score = models.FloatField()

    def __str__(self):
        return str(self.pk)

class Complaint(models.Model):
  student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='complaint_results')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='complaint_results')
  score = models.IntegerField(default=0)
  subject = models.CharField(max_length=255)
  message = models.TextField()

  def __str__(self):
    return self.subject