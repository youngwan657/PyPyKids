from django.shortcuts import render
from list.views.common import *
from django.db.models import Q, Sum


def welcome(request):
    return categories(request)


def categories(request):
    context = {}
    username = get_profile(request, context)

    if username != "":
        customuser = CustomUser.objects.get(name=username)
        user_point, created = UserPoint.objects.get_or_create(customuser=customuser, date=date.today(),
                                                               pointtype__name="DailyCheckIn")
        if created:
            pointtype = PointType.objects.get(name="DailyCheckIn")
            user_point.customuser = customuser
            user_point.pointtype = pointtype
            user_point.save()

            customuser.point += pointtype.point
            context['profile_point'] += pointtype.point
            customuser.save()
            context['daily_check_in'] = True

    quizzes = Quiz.objects.order_by('order').filter(visible=True)
    unsolved_quizzes = quizzes
    difficulties = Difficulty.objects.order_by('id')
    for difficulty in difficulties:
        difficulty.set_name_url()
    context['difficulties'] = difficulties

    if username != "":
        answers = Answer.objects.filter(customuser=customuser)
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

    # Today's Quiz
    today_quiz = unsolved_quizzes.order_by('order').first()
    context['quiz'] = today_quiz.set_title_url().set_pretty_code()
    context['difficulty'] = today_quiz.category.difficulty.set_name_url()
    context['category'] = today_quiz.category.set_name_url()

    # New Video for non-login user
    if username == "":
        new_video = Quiz.objects.get(id=139)
        context['quiz'] = new_video.set_title_url()

    score = QuizScore.objects.filter(quiz__order=today_quiz.order).aggregate(Sum('score'))['score__sum']
    context['score'] = score if score != None else 0

    for difficulty in difficulties:
        categories = Category.objects.order_by('order').filter(difficulty=difficulty.id, visible=True)
        answers = Answer.objects.filter(customuser__name=username, right=Right.RIGHT.value)
        for category in categories:
            quizzes = Quiz.objects.filter(category_id=category.id, visible=True)
            category.total_quiz = quizzes.count()
            category.unsolved_quiz = quizzes.count() - len(answers.filter(quiz_id__in=quizzes))
            category.solved_quiz = category.total_quiz - category.unsolved_quiz
            category.set_name_url()

        context["level" + str(difficulty.id)] = categories

    context['page_title'] = "Python for Kids"
    context['page_description'] = "PyPykids is an online Python coding service. Python is perfect for kids to think logically."
    context['page_keyword'] = "Python for Kids, Python tutorial for Kids, Learning Python"

    return render(request, 'list/categories.html', context)
