from django.shortcuts import render
from list.views.common import *
from django.db.models import Q, Sum


def categories(request):
    context = {}
    quizzes = Quiz.objects.order_by('order').filter(visible=True)
    unsolved_quizzes = quizzes
    difficulties = Difficulty.objects.order_by('id')
    context['difficulties'] = difficulties
    username = get_username(request)
    context['username'] = username

    if request.user.is_authenticated:
        answers = Answer.objects.filter(name=username)
        total_quizzes = Quiz.objects.count()
        right_quizzes = answers.filter(right=Right.RIGHT.value).count()
        wrong_quizzes = answers.filter(Q(right=Right.WRONG.value) | Q(right=Right.WAS_RIGHT.value)).count()
        unsolved_quizzes = get_unsolved_quizzes(username)

        # Chart
        now = date.today() + timedelta(days=+1)
        labels, counts = [], []
        for i in range(0, MONTH):
            now += timedelta(days=-1)
            if now.strftime("%d") == "01" or i == 30:
                labels.insert(0, now.strftime("%b %d"))
            else:
                labels.insert(0, now.strftime("%d"))
            count = answers \
                .filter(date=now) \
                .filter(Q(right=Right.RIGHT.value) | Q(right=Right.WAS_RIGHT.value)) \
                .count()
            counts.insert(0, count)

        context['labels'] = labels
        context['counts'] = counts

        # Circle chart
        context['total_quiz'] = total_quizzes
        context['accepted_quiz'] = right_quizzes
        context['wrong_quiz'] = wrong_quizzes
        context['not_try_quiz'] = total_quizzes - right_quizzes - wrong_quizzes

        # Badge
        context['badges'] = Badge.objects.filter(customuser__name=username)

    # Today's Question
    today_quiz = unsolved_quizzes.order_by('?').first()
    context['quiz'] = today_quiz.set_title_url()
    context['difficulty'] = today_quiz.category.difficulty
    context['category'] = today_quiz.category.name

    score = QuizScore.objects.filter(quiz__order=today_quiz.order).aggregate(Sum('score'))['score__sum']
    context['score'] = score if score != None else 0

    for difficulty in difficulties:
        categories = Category.objects.order_by('order').filter(difficulty=difficulty.id, visible=True)
        all_quizzes = Quiz.objects;
        answers = Answer.objects.filter(name=username, right=Right.RIGHT.value)
        for category in categories:
            quizzes = all_quizzes.filter(category__name=category.name, visible=True)
            category.total_quiz = quizzes.count()
            category.unsolved_quiz = quizzes.count()
            for quiz in quizzes:
                if len(answers.filter(quiz__order=quiz.order)) == Right.RIGHT.value:
                    category.unsolved_quiz -= 1
            category.solved_quiz = category.total_quiz - category.unsolved_quiz

        context["level" + str(difficulty.id)] = categories

    context['quiz_name'] = 'TODAY QUIZ'
    return render(request, 'list/categories.html', context)
