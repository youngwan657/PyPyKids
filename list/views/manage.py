from django.shortcuts import render

from list.views.common import *


def manage(request):
    quizzes = Quiz.objects.all()
    for quiz in quizzes:
        quiz.set_title_url()
    testcases = Testcase.objects.all()
    answers = Answer.objects.all()

    context = {
        'quizzes': quizzes,
        'testcases': testcases,
        'answers': answers,
    }
    return render(request, 'list/manage.html', context)



# TODO:: Answer history

# TODO:: point or score
# TODO:: modified date for answer
# TODO:: like for answer
# TODO:: comment for answer
# TODO:: show other people's answer
# TODO:: profile page
# TODO:: search
