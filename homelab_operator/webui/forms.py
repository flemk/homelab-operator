'''Forms for the web UI of the homelab operator project.'''

from django.forms import ModelForm, DateTimeInput
from django.utils.html import format_html
from .models import Server, Service, Network, WOLSchedule

class ServerForm(ModelForm):
    '''Form for creating and updating Server instances.'''
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(ServerForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True

        self.fields['ssh_username'].label = 'SSH Username'
        self.fields['ssh_password'].label = 'SSH Password'
        self.fields['ssh_password'].help_text = format_html(
            '<span class="soft error">SSH credentials are stored in plain text.' + \
                'Use this feature with caution.</span>')

    class Meta:
        model = Server
        fields = '__all__'

class ServiceForm(ModelForm):
    '''Form for creating and updating Service instances.'''
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)

    # TODO only display servers that belong to the user

    class Meta:
        model = Service
        fields = '__all__'

class NetworkForm(ModelForm):
    '''Form for creating and updating Network instances.'''
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(NetworkForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True

    class Meta:
        model = Network
        fields = '__all__'

class WOLScheduleForm(ModelForm):
    '''Form for creating and updating WOLSchedule instances.'''
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(WOLScheduleForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True

    class Meta:
        model = WOLSchedule
        fields = '__all__'
        widgets = {
            'schedule_time': DateTimeInput(attrs={'type': 'datetime-local'}),
        }
