from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from datetime import datetime, date, timedelta
import subprocess
import os

from django.db.models import Q

from .models import Quiz, Answer, Testcase, Category, Difficulty, CustomUser, Badge
from .right import Right

# login, register
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

MONTH = 31


def all_category(request):
    context = {}
    quizzes = Quiz.objects.order_by('order').filter(visible=True)
    unsolved_quizzes = quizzes
    difficulties = Difficulty.objects.order_by('id')
    context['difficulties'] = difficulties
    username = _get_username(request)
    context['username'] = username

    if request.user.is_authenticated:
        answers = Answer.objects.filter(name=username)
        total_quizzes = Quiz.objects.count()
        right_quizzes = answers.filter(right=Right.RIGHT.value).count()
        wrong_quizzes = answers.filter(Q(right=Right.WRONG.value) | Q(right=Right.WRONG_BUT_RIGHT_BEFORE.value)).count()
        unsolved_quizzes = _get_unsolved_quizzes(username)

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
                .filter(Q(right=Right.RIGHT.value) | Q(right=Right.WRONG_BUT_RIGHT_BEFORE.value)) \
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
    context['quiz'] = today_quiz
    context['difficulty'] = today_quiz.category.difficulty
    context['category'] = today_quiz.category.name

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
    context['quiz_image'] = 'theme/devices/airpods.svg'
    return render(request, 'list/all_category.html', context)


# TODO:: category master
def badge(request):
    context = {
        'username': _get_username(request),
        'badges': Badge.objects.all(),
    }
    return render(request, 'list/badge.html', context)


def category(request, category):
    context = {}
    quizzes = Quiz.objects.filter(category__name=category, visible=True).order_by('order')
    right_quizzes = 0
    right_percent = 0

    username = _get_username(request)
    context['username'] = username
    if username != "":
        answers = Answer.objects.filter(name=username)
        right_quizzes = 0
        for quiz in quizzes:
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


def show(request, quiz_order):
    context = {}
    username = _get_username(request)
    context['username'] = username

    answers = Answer.objects.filter(name=username)

    quiz = get_object_or_404(Quiz, order=quiz_order)
    # TODO:: 404 when visible is False

    right_modal = request.GET.get('right_modal')
    answer = answers.filter(quiz__order=quiz_order).first()

    # default answer header
    context['user_answer'] = quiz.answer_header
    if answer:
        context['user_answer'] = answer.answer
        context['answer'] = answer

    context['next'] = _get_unsolved_quizzes(username, quiz_order).first()
    context['difficulty'] = quiz.category.difficulty
    context['category'] = quiz.category.name
    context['new_badge'] = _add_badge(username)
    context['quiz'] = quiz
    context['right_modal'] = right_modal
    context['quiz_name'] = quiz_order
    # TODO:: change to configurable image for quiz
    context['quiz_image'] = 'theme/devices/airpods.svg'

    return render(request, 'list/show.html', context)


# TODO:: check the object input
# TODO:: dynamic function name depending on quiz.
def answer(request, quiz_order):
    quiz = get_object_or_404(Quiz, order=quiz_order)
    testcases = Testcase.objects.filter(quiz__order=quiz_order)
    answer, created = Answer.objects.get_or_create(quiz__order=quiz_order, name=request.user.username)
    answer.quiz = quiz
    answer.answer = request.POST['answer']
    if answer.right != Right.RIGHT.value and answer.right != Right.WRONG_BUT_RIGHT_BEFORE.value:
        answer.date = datetime.now()

    if quiz.quiz_type.name == "Code":
        _check_answer(testcases, answer)
    elif quiz.quiz_type.name == "Answer" or quiz.quiz_type.name == "MultipleChoice":
        # answer
        if answer.answer.replace(" ", "").strip() == testcases[0].expected_answer:
            answer.right = Right.RIGHT.value
            answer.output = ""
        else:
            if answer.right == Right.RIGHT.value or answer.right == Right.WRONG_BUT_RIGHT_BEFORE.value:
                answer.right = Right.WRONG_BUT_RIGHT_BEFORE.value
            else:
                answer.right = Right.WRONG.value
            answer.output = answer.answer

    answer.save()

    return HttpResponseRedirect('/' + str(quiz.order) + "?right_modal=" + str(answer.right))


def playground(request):
    context = {}
    context["username"] = _get_username(request)
    if request.method == "POST":
        f = open("playground.py", "w+")
        code = request.POST['code']
        f.write(code)
        f.close()
        try:
            process = subprocess.Popen(['python', 'playground.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            outs, errs = process.communicate(timeout=1)
            stdout = outs.decode("utf-8")
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "TIMEOUT ERROR"

        context = {
            'code': code,
            'stdout': stdout,
        }

    return render(request, 'list/playground.html', context)


def show_all_quiz(request):
    quizzes = Quiz.objects.all()
    testcases = Testcase.objects.all()
    answers = Answer.objects.all()

    context = {
        'quizzes': quizzes,
        'testcases': testcases,
        'answers': answers,
    }
    return render(request, 'list/all_quiz.html', context)


def signup(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            custom_user = CustomUser.objects.create(name=user.username)
            custom_user.badges.add(Badge.objects.get(order=0))
            custom_user.save()
            login(request, user)
            return redirect("/")

    context = {
        'form': form,
    }
    return render(request, 'list/signup.html', context)


def signout(request):
    logout(request)
    return redirect("/")


def signin(request):
    context = {}
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                context['login_error'] = 1
        else:
            context['login_error'] = 1

    form = AuthenticationForm()
    context['form'] = form
    return render(request, "list/signin.html", context)


# TODO:: Answer history

def about(request):
    user = CustomUser.objects.count()
    quiz = Quiz.objects.count()
    badge = Badge.objects.count()

    context = {
        'username': _get_username(request),
        'user': user,
        'quiz': quiz,
        'badge': badge,
    }
    return render(request, 'list/about.html', context)


# private
def _get_username(request):
    if request.user.is_authenticated:
        return request.user.username
    return ""


# TODO:: dynamic file name
def _check_answer(testcases, answer):
    f = open("solution.py", "w+")
    f.write(answer.answer)
    f.close()

    for testcase in testcases:
        output = "None"
        stdout = ""
        try:
            process = subprocess.Popen(['python', 'checking.py'] + testcase.test.split("\n"), stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            outs, errs = process.communicate(timeout=1)
            stdout = outs.decode("utf-8")
            if os.path.exists("checking_answer"):
                f = open("checking_answer", "r")
                output = f.read().strip()
                f.close()
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "TIMEOUT ERROR"

        testcase.expected_answer = testcase.expected_answer.replace("\r\n", "\n")
        if str(output) != testcase.expected_answer.strip():
            answer.right = Right.WRONG.value
            answer.testcase = testcase.test
            answer.expected_answer = testcase.expected_answer
            answer.output = output
            answer.stdout = stdout
            return

    answer.right = Right.RIGHT.value
    answer.testcase = ""
    answer.expected_answer = ""
    answer.output = ""
    answer.stdout = ""


# TODO:: move to check when solving quiz.
def _add_badge(username):
    if username == "":
        return None

    custom_user = CustomUser.objects.get(name=username)
    answers = Answer.objects.filter(name=username, right=Right.RIGHT.value)
    untaken_badges = Badge.objects.filter(~Q(customuser__name=username))

    # day streak
    now = date.today() + timedelta(days=+1)
    day_streak = 0
    for i in range(0, MONTH):
        now += timedelta(days=-1)
        if answers.filter(date=now, right=Right.RIGHT.value).count() == 0:
            day_streak = i
            break

    for badge in untaken_badges:
        if badge.type.name == "DayStreak" and badge.value <= day_streak:
            custom_user.badges.add(badge)
            custom_user.save()
            return badge

    # quiz per day
    quiz_per_day = answers.filter(date=date.today()).count()
    for badge in untaken_badges:
        if badge.type.name == "QuizPerDay" and badge.value <= quiz_per_day:
            custom_user.badges.add(badge)
            custom_user.save()
            return badge

    # total quiz
    total_quiz = answers.count()
    for badge in untaken_badges:
        if badge.type.name == "TotalQuiz" and badge.value <= total_quiz:
            custom_user.badges.add(badge)
            custom_user.save()
            return badge

    return None


def _get_unsolved_quizzes(username, quiz_order=-1):
    quizzes = Quiz.objects.filter(visible=True, order__gt=quiz_order).order_by('order')
    if len(quizzes) == 0:
        quizzes = Quiz.objects.filter(visible=True).order_by('order')
    answers = Answer.objects.filter(name=username)
    for answer in answers:
        if answer.right == Right.RIGHT.value:
            quizzes = quizzes.filter(~Q(order=answer.quiz.order))

    return quizzes



# TODO:: split multiple view per function.
# TODO:: like button only for the kids who solved person.
# TODO:: chat with admin
# TODO:: code mirror editor
