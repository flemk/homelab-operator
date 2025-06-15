from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse
from datetime import datetime
from .models import Server, WOLSchedule

def rate_limit(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR')
        key = f"rate_limit_is_online_{ip}"
        count = cache.get(key, 0)
        if count >= 120:
            return HttpResponse("Too Many Requests", status=429)
        cache.set(key, count + 1, timeout=60)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def update_uptime_statistics():
    for server in Server.objects.all():
        if server.uptime_statistic.first():
            uptime_statistic = server.uptime_statistic.first()
            if not uptime_statistic.initialized:
                uptime_statistic.initialize_matrix()

            now = datetime.now()
            hour = now.hour
            day = now.weekday()
            is_online = server.is_online()

            print(server, is_online, now)

            uptime_statistic.update_uptime(day, hour, is_online)

def process_schedules():
    now = datetime.now()
    minute_window = [(now.minute + offset) % 60 for offset in range(-5, 6)]
    schedules = WOLSchedule.objects.filter(
        enabled=True,
        schedule_time__hour=now.hour,
        schedule_time__minute__in=minute_window
    )

    for schedule in schedules.all():
        if schedule.repeat:
            if schedule.repeat_type == 'daily':
                # schedule should be executed every day, no action needed
                continue
            if schedule.repeat_type == 'weekly':
                if schedule.schedule_time.weekday() != now.weekday():
                    schedules.exclude(id=schedule.id)
            elif schedule.repeat_type == 'monthly':
                if schedule.schedule_time.month != now.month \
                    and schedule.schedule_time.day != now.day:
                    schedules.exclude(id=schedule.id)
        else:
            if schedule.schedule_time.date() != now.date():
                schedules.exclude(id=schedule.id)

    for schedule in schedules:
        server = schedule.server
        if server:
            if not server.auto_wake:
                continue
            if not server.auto_wake:
                continue
            if schedule.type == 'WAKE':
                response = server.wake()
                if response is False:
                    print(f"Magic packet sent to {server.name}" + \
                          f"(Scheduled by {schedule.user.username})")
                    print(f"Magic packet sent to {server.name}" + \
                          f"(Scheduled by {schedule.user.username})")
                else:
                    print(f"Failed to send magic packet to {server.name}: {response}")
            elif schedule.type == 'SHUTDOWN':
                response = server.shutdown()
                if response is True:
                    print(f"Shutdown command sent to {server.name} " + \
                          f"(Scheduled by {schedule.user.username})")
                    print(f"Shutdown command sent to {server.name} " + \
                          f"(Scheduled by {schedule.user.username})")
                else:
                    print(f"Failed to send shutdown command to {server.name}: {response}")
        else:
            print(f"Server not found for schedule ID {schedule.id}")

    return HttpResponse("OK", status=200)
