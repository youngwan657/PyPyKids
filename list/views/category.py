from django.shortcuts import render

from list.views.common import *


def category(request, category):
    context = {}
    category = category.replace("-", " ")
    quizzes = Quiz.objects.filter(category__name=category, visible=True).order_by('order')

    username = get_profile(request, context)

    for quiz in quizzes:
        quiz.set_title_url()

    if username != "":
        answers = Answer.objects.filter(customuser__name=username)
        for quiz in quizzes:
            answer = answers.filter(quiz__order=quiz.order)
            quiz.right = 0
            if len(answer) > 0:
                quiz.right = answer[0].right

    context["difficulty"] = quizzes[0].category.difficulty.set_name_url()
    context["category"] = category
    context["quizzes"] = quizzes
    context['page_title'] = category
    context['page_description'] = quizzes[0].category.desc
    return render(request, 'list/category.html', context)

