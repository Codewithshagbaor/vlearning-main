from django.urls import path, include

from . import views, instructor_views, student_views
instructor_urlpatterns = [
    path('courses/', instructor_views.instructor_course_list, name="instructor_courses"),
    path('course/create/', instructor_views.create_course, name='create_course'),
    path('course/<int:course_id>/edit/', instructor_views.edit_course, name='edit_course'),
    path('course/<int:course_id>/delete/', instructor_views.delete_course, name='delete_course'),
    path('course/<int:course_id>/', instructor_views.view_course, name='view_course'),
    path('course/<int:course_id>/students/', instructor_views.manage_students, name='manage_students'),
    path('course/<int:course_id>/module/create/', instructor_views.create_module, name='create_module'),
    path('module/<int:module_id>/edit/', instructor_views.edit_module, name='edit_module'),
    path('module/<int:module_id>/delete/', instructor_views.delete_module, name='delete_module'),
    path('unit/<int:module_id>/create/', instructor_views.create_unit, name='create_unit'),
    path('unit/<int:unit_id>/edit/', instructor_views.edit_unit, name='edit_unit'),
    path('material/<int:unit_id>/create/', instructor_views.create_material, name='create_material'),
    path('material/<int:material_id>/edit/', instructor_views.edit_material, name='edit_material'),
    path('material/<int:material_id>/delete/', instructor_views.delete_material, name='delete_material'),
    path('test/<int:course_id>/create/', instructor_views.create_test, name='create_test'),
    path('Test/<int:course_id>/<int:pk>/view/', instructor_views.quiz_view_admin, name='quiz_view_admin'),
    path('create/<int:quiz_id>/questions', instructor_views.create_question, name='create_question'),
    path('edit_question/<int:quiz_id>/questions/<int:question_id>/edit/', instructor_views.edit_question, name='edit_question'),
    path('all_complaints/', instructor_views.all_complaints, name="all_complaints"),
    path('complaints/<int:complaint_id>/delete/', instructor_views.delete_complaints_admin, name='delete_complaints_admin'),
    path('student_list/', instructor_views.teacher_student_list, name="teacher_student_list"),



]

student_urlpatterns = [
    path('courses/', student_views.student_courses, name='student_courses'),
    path('courses/enroll/<int:course_id>/', student_views.enroll_course, name='enroll_course'),
    path('courses/unenroll/<int:course_id>/', student_views.unenroll_course, name='unenroll_course'),
    path('study/<int:course_id>/', student_views.study, name='study-page'),
    path('Test/<int:course_id>/<int:pk>/', student_views.quiz_view, name='test_detail'),
    path('Test/<int:course_id>/<int:pk>/data/', student_views.quiz_data_view, name='quiz-data-view'),
    path('Test/<int:course_id>/<int:pk>/save/', student_views.save_quiz_view, name='save-view'),
    path('complaint_submit/', student_views.submit_complaint, name='submit_complaint'),
    path('result/', student_views.user_results, name="user_results"),
    path('all_complaints_student/', student_views.all_complaints_student, name="all_complaints_student"),
]
urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.login_page, name='login'),
    path('auth/register/', views.register_student, name='register_student'),
    path('api/login/', views.login_handler, name='login_handler'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/logout/', views.logout_handler, name='logout_handler'),
    path('ai-driven/', views.ai_chat_view, name='ai_chat_view'),
    path('instructor/', include(instructor_urlpatterns)),
    path('student/', include(student_urlpatterns)),
]