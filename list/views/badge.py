# TODO:: category master
from django.shortcuts import render

from list.views.common import *


def badge(request):
    context = {}
    get_profile(request, context)

    context['badges'] = Badge.objects.all()
    return render(request, 'list/badge.html', context)
