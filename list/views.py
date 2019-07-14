from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import datetime

from .models import Quiz


def index(request):
    quizs = Quiz.objects.order_by('id')
    context = {'quizs': quizs, 'filter': 1000000}
    return render(request, 'list/index.html', context)


def list(request, quiz_id):
    quizs = Quiz.objects.order_by('id')
    context = {'quizs': quizs, 'filter': quiz_id}
    return render(request, 'list/index.html', context)


def show(request, quiz_id):
    quiz = Quiz.objects.filter(id=quiz_id)
    right = request.GET.get('right')
    context = {'quiz': quiz[0], 'right': right}
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

