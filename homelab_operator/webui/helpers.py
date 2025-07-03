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
    now = datetime.now()
    hour = now.hour
    day = now.weekday()

    for server in Server.objects.all():
        if server.uptime_statistic.first():
            uptime_statistic = server.uptime_statistic.first()
            if not uptime_statistic.initialized:
                uptime_statistic.initialize_matrix()

            is_online = server.is_online()
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
        if schedule.server.auto_wake is False:
            schedules = schedules.exclude(id=schedule.id)
            continue
        if schedule.repeat:
            if schedule.repeat_type == 'daily':
                # schedule should be executed every day, no action needed
                continue
            if schedule.repeat_type == 'weekly':
                if schedule.schedule_time.weekday() != now.weekday():
                    schedules = schedules.exclude(id=schedule.id)
            elif schedule.repeat_type == 'monthly':
                if schedule.schedule_time.day != now.day:
                    schedules = schedules.exclude(id=schedule.id)
            else:
                schedules = schedules.exclude(id=schedule.id)
                continue
        else:
            if schedule.schedule_time.date() != now.date():
                schedules = schedules.exclude(id=schedule.id)

    for schedule in schedules:
        log_entry = f'[{now}] - SCHEDULE: No action performed for schedule {schedule.id}'
        server = schedule.server
        if server:
            if schedule.type == 'WAKE':
                response = server.wake()
                if response is False:
                    log_entry = f'[{now}] - WAKE: Magic packet sent to {server.name} ' + \
                                f'(Scheduled by {schedule.user.username})'
                else:
                    log_entry = f'[{now}] - WAKE: Failed to send magic packet to ' + \
                                f'{server.name}: {response}'
            elif schedule.type == 'SHUTDOWN':
                response = server.shutdown()
                if response is False:
                    log_entry = f'[{now}] - SHUTDOWN: Shutdown command sent to {server.name} ' + \
                                f'(Scheduled by {schedule.user.username})'
                else:
                    log_entry = f'[{now}] - SHUTDOWN: Failed to send shutdown command to ' + \
                                f'{server.name}: {response}'
        else:
            log_entry = f'[{now}] - SCHEDULE: No server found for schedule {schedule.id}'

        if schedule.enable_log:
            schedule.logs = (schedule.logs or '') + log_entry + '\n'
            schedule.save()

    return HttpResponse("OK", status=200)
