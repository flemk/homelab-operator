from .models import AppState

def app_state(request):
    return {'app_state': AppState.load()}
