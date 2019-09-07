from django.shortcuts import render
from list.views.common import *


def about(request):
    user = CustomUser.objects.count()
    quiz = Quiz.objects.count()
    badge = Badge.objects.count()

    context = {
        'username': get_username(request),
        'user': user,
        'quiz': quiz,
        'badge': badge,
    }
    return render(request, 'list/about.html', context)
