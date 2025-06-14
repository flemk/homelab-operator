'''Forms for the web UI of the homelab operator project.'''

from django.forms import ModelForm, DateTimeInput
from .models import Server, Service, Network, WOLSchedule, ShutdownURLConfiguration, Homelab, \
    Wiki, UserProfile

class UserProfileForm(ModelForm):
    '''Form for creating and updating UserProfile instances.'''
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(UserProfileForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True

    class Meta:
        model = UserProfile
        fields = '__all__'

class ServerForm(ModelForm):
    '''Form for creating and updating Server instances.'''
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(ServerForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True

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

class ShutdownURLConfigurationForm(ModelForm):
    '''Form for creating and updating ShutdownURLConfiguration instances.'''
    def __init__(self, *args, **kwargs):
        server = kwargs.pop('server', None)

        super(ShutdownURLConfigurationForm, self).__init__(*args, **kwargs)

        if server:
            self.fields['server'].initial = server
            self.fields['server'].disabled = True

    class Meta:
        model = ShutdownURLConfiguration
        fields = '__all__'

class HomelabForm(ModelForm):
    '''Form for creating and updating Homelab instances.'''
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(HomelabForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True

    class Meta:
        model = Homelab
        fields = '__all__'

class WikiForm(ModelForm):
    '''Form for creating and updating Wiki instances.'''
    def __init__(self, *args, **kwargs):
        homelab = kwargs.pop('homelab', None)

        super(WikiForm, self).__init__(*args, **kwargs)

        if homelab:
            self.fields['homelab'].initial = homelab
            self.fields['homelab'].disabled = True

    class Meta:
        model = Wiki
        fields = '__all__'
