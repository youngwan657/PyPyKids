from django.shortcuts import render

from list.views.common import *


def manage(request):
    testcases = Testcase.objects.all()
    answers = Answer.objects.all()

    quizzes = Quiz.objects.all()
    error_quizzes = []
    for quiz in quizzes:
        quiz.set_title_url().convert_explanation()
        if testcases.filter(quiz_id=quiz.id).exists() == False:
            error_quizzes.append(quiz)

    context = {
        'error_quizzes': error_quizzes,
        'quizzes': quizzes,
        'testcases': testcases,
        'answers': answers,
    }

    return render(request, 'list/manage.html', context)



# TODO:: Answer history

# TODO:: like, comment for answer
# TODO:: profile page
# TODO:: search
