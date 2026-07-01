from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import Reminder, SleepEntry


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'myApp/signup.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'myApp/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    entries = SleepEntry.objects.filter(user=request.user).order_by('-date')[:10]
    summary = SleepEntry.summarize_entries(SleepEntry.objects.filter(user=request.user))
    reminder = Reminder.objects.filter(user=request.user).first()

    if request.method == 'POST':
        if 'date' in request.POST:
            SleepEntry.objects.create(
                user=request.user,
                date=request.POST['date'],
                bedtime=request.POST['bedtime'],
                wake_time=request.POST['wake_time'],
                hours_slept=request.POST['hours_slept'],
                note=request.POST.get('note', ''),
            )
        elif 'reminder_time' in request.POST:
            reminder_time = request.POST['reminder_time']
            reminder_enabled = request.POST.get('enabled') == 'on'
            if reminder:
                reminder.bedtime = reminder_time
                reminder.enabled = reminder_enabled
                reminder.save()
            else:
                Reminder.objects.create(user=request.user, bedtime=reminder_time, enabled=reminder_enabled)

        return redirect('home')

    context = {
        'entries': entries,
        'summary': summary,
        'user': request.user,
        'reminder': reminder,
    }
    return render(request, 'myApp/home.html', context)
