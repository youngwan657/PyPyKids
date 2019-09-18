from django.shortcuts import render

from list.views.common import *


def category(request, category):
    context = {}
    quizzes = Quiz.objects.filter(category__name=category, visible=True).order_by('order')
    right_quizzes = 0
    right_percent = 0

    username = get_username(request)
    context['username'] = username
    if username != "":
        answers = Answer.objects.filter(name=username)
        right_quizzes = 0
        for quiz in quizzes:
            quiz.set_title_url()
            answer = answers.filter(quiz__order=quiz.order)
            quiz.right = 0
            if len(answer) > 0:
                quiz.right = answer[0].right
            if quiz.right == 1:
                right_quizzes += 1

        if quizzes.count() == 0:
            right_percent = 100
        else:
            right_percent = right_quizzes / quizzes.count() * 100

    context["difficulty"] = quizzes[0].category.difficulty
    context["category"] = category
    context["quizzes"] = quizzes
    context["total_quiz"] = quizzes.count()
    context["right"] = right_quizzes
    context["right_percent"] = right_percent
    return render(request, 'list/category.html', context)

