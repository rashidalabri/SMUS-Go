from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from .models import Mission, CompletedMission, MissionKey, User, Grade
from django.utils import timezone
from django.views.generic import ListView
import pagan
from .forms import SignUpForm

from projectspirit.settings import MEDIA_DIR, MEDIA_URL


def index(request):
    return HttpResponse('Hi')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            avatar = pagan.Avatar(username, pagan.SHA512)
            avatar.save(MEDIA_DIR, username)

            user.avatar = username + '.png'
            user.save()

            login(request, user)
            return redirect('spiritdashboard:dashboard')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'spiritdashboard/register.html', context=context)


@login_required
def dashboard(request):
    context = {
        'missions': Mission.objects.all(),
        'grade': request.user.grade,
    }
    return render(request, 'spiritdashboard/dashboard.html', context=context)


@login_required
def claim_key(request, key):

    # Validates key string
    if len(key) == 10 and MissionKey.objects.filter(key=key):
        mission = MissionKey.objects.filter(key=key)[0].mission

        # Checks if mission is not expired or in the future, and that it has not been completed before
        if not mission.is_future() and not mission.is_expired() and not CompletedMission.objects.filter(mission=mission, user=request.user):

            # Creates CompletedMission object and saves it to database
            completed_mission = CompletedMission(
                mission=mission, user=request.user)
            completed_mission.save()

            # Adds points for the user
            request.user.points += mission.value

            # Adds points for the user's grade (if it exists)
            if request.user.grade is not None:
                request.user.grade.points += mission.value

            request.user.save()
            request.user.grade.save()

            return render(request, 'spiritdashboard/completed.html', context={'mission': mission})
    
    return HttpResponseBadRequest(reason='Invalid key, or you have already completed the mission.')


def completed(request):
    return render(request, 'spiritdashboard/completed.html')


class UserLeaderboard(ListView):
    model = User
    template_name = 'spiritdashboard/leaderboards/user.html'
    queryset = User.objects.order_by('-points')[:10]


class GradeLeaderboard(ListView):
    model = Grade
    template_name = 'spiritdashboard/leaderboards/grade.html'
    queryset = Grade.objects.order_by('-points')[:10]
