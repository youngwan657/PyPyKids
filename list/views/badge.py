# TODO:: category master
from django.shortcuts import render

from list.views.common import *


def badge(request):
    context = {}
    username = get_profile(request, context)
    if username == "":
        context['my_badges'] = Badge.objects.all()
    else:
        context['my_badges'] = Badge.objects.filter(customuser__name=username)
        context['gray_badges'] = Badge.objects.exclude(customuser__name=username)
    return render(request, 'list/badge.html', context)
