from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import datetime

from .models import Quiz

def index(request):
    quizs = Quiz.objects.order_by('-question_date')[:5]
    context = {'quizs': quizs}
    return render(request, 'list/index.html', context)

def answer(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz.answer = request.POST['answer']
    quiz.answer_date = datetime.datetime.now()
    quiz.save()

    quizs = Quiz.objects.order_by('-question_date')[:5]
    return HttpResponseRedirect('/')
