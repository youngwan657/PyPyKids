from django.shortcuts import render

from list.views.common import *


def category(request, category):
    context = {}
    quizzes = Quiz.objects.filter(category__name=category, visible=True).order_by('order')

    username = get_username(request)
    context['username'] = username

    for quiz in quizzes:
        quiz.set_title_url()

    if username != "":
        answers = Answer.objects.filter(customuser__name=username)
        for quiz in quizzes:
            answer = answers.filter(quiz__order=quiz.order)
            quiz.right = 0
            if len(answer) > 0:
                quiz.right = answer[0].right

    context["difficulty"] = quizzes[0].category.difficulty
    context["category"] = category
    context["quizzes"] = quizzes
    return render(request, 'list/category.html', context)

