from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import datetime

from .models import Quiz


def list(request):
    quizs = Quiz.objects.order_by('id')
    right_quizs = quizs.filter(right=1).count()
    wrong_quizs = quizs.filter(right=-1).count()
    context = {
        'quizs': quizs,
        'total_quiz': quizs.count(),
        'right': right_quizs,
        'wrong': wrong_quizs,
        'right_percent': right_quizs / quizs.count() * 100,
        'wrong_percent': wrong_quizs / quizs.count() * 100,
    }
    return render(request, 'list/list.html', context)


def show(request, quiz_id):
    quiz = Quiz.objects.filter(id=quiz_id)
    next = Quiz.objects.filter(visible=True).filter(id__gt=quiz_id).first()

    # 1: right, -1: wrong, 0: default
    right = request.GET.get('right')
    context = {
        'quiz': quiz[0],
        'right': right,
        'next': next,
    }
    return render(request, 'list/show.html', context)


def answer(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz.answer = request.POST['answer']
    quiz.answer_date = datetime.datetime.now()
    if quiz.correct_answer != "":
        if quiz.answer.replace(" ", "").strip() == quiz.correct_answer:
            quiz.right = 1
        else:
            quiz.right = -1
    quiz.save()

    return HttpResponseRedirect('/' + str(quiz.id) + "?right=" + str(quiz.right))
