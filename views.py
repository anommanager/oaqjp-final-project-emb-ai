from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Question, Choice, Submission


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    submission = Submission.objects.create(enrollment=enrollment)
    
    for key, values in request.POST.items():
        if key.startswith('choice'):
            for choice_id in request.POST.getlist(key):
                choice = Choice.objects.get(pk=choice_id)
                submission.choices.add(choice)
    submission.save()
    
    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result',
                args=(course_id, submission.id))
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_score = 0
    selected_ids = submission.choices.values_list('id', flat=True)
    
    for question in course.question_set.all():
        if question.is_get_score(selected_ids):
            total_score += question.grade
    
    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'total_score': total_score,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
