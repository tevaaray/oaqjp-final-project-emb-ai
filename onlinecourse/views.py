from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    selected_ids = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            selected_ids.append(int(value))
            
    enrollment = request.user.enrollment_set.get(course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    for choice_id in selected_ids:
        choice = Choice.objects.get(pk=choice_id)
        submission.choices.add(choice)
        
    return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_score = 0
    max_score = 0
    
    questions = course.question_set.all()
    
    # Собираем все ID выбранных пользователем вариантов в список
    selected_ids = list(submission.choices.values_list('id', flat=True))

    for question in questions:
        max_score += question.grade
        q_choice_ids = [choice.id for choice in submission.choices.filter(question=question)]
        if question.is_get_score(q_choice_ids):
            total_score += question.grade
            
    context = {
        'course': course,
        'submission': submission,
        'total_score': total_score,
        'max_score': max_score,
        'selected_ids': selected_ids, # Требуется по критериям проверки
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)