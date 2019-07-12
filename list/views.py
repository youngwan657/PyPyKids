from django.shortcuts import render
from django.urls import reverse

from .models import Quiz

def index(request):
    quizzes = Quiz.objects.order_by('-question_date')[:5]
    context = {'quizzes': quizzes}
    return render(request, 'list/index.html', context)

def answer(request, quiz):
    print(quiz.quiz_id)
    question = get_object_or_404(Quiz, quiz_id=quiz.quiz_id)
    question.answer = quiz.answer
    question.update()

    quizzes = Quiz.objects.order_by('-question_date')[:5]
    context = {'quizzes': quizzes}
    return render(request, 'list/index.html', context)
