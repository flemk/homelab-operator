'''Forms for the web UI of the homelab operator project.'''

from django.forms import ModelForm, DateTimeInput, BooleanField, CharField, Textarea, ModelMultipleChoiceField, CheckboxSelectMultiple
from .models import Server, Service, Network, WOLSchedule, ShutdownURLConfiguration, Homelab, \
    Wiki, UserProfile, Ingress
from .widgets import HoCheckbox
from django.utils.safestring import mark_safe

class UserProfileForm(ModelForm):
    '''Form for creating and updating UserProfile instances.'''
    show_wiki = BooleanField(widget=HoCheckbox(
        label=UserProfile._meta.get_field('show_wiki').help_text), required=False, label='')
    show_networks = BooleanField(widget=HoCheckbox(
        label=UserProfile._meta.get_field('show_networks').help_text), required=False, label='')
    show_ingress = BooleanField(widget=HoCheckbox(
        label=UserProfile._meta.get_field('show_ingress').help_text), required=False, label='')
    dark_mode = BooleanField(widget=HoCheckbox(
        label=UserProfile._meta.get_field('dark_mode').help_text), required=False, label='')

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
    auto_wake =  BooleanField(
        widget=HoCheckbox(
            label=Server._meta.get_field('auto_wake').help_text), required=False, label='')

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
    enabled = BooleanField(
        widget=HoCheckbox(
            label=WOLSchedule._meta.get_field('enabled').help_text), required=False, label='')
    repeat = BooleanField(
        widget=HoCheckbox(
            label=WOLSchedule._meta.get_field('repeat').help_text), required=False, label='')
    enable_log = BooleanField(
        widget=HoCheckbox(
            label=WOLSchedule._meta.get_field('enable_log').help_text), required=False, label='')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(WOLScheduleForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True

        self.fields['logs'] = CharField(
            initial=self.instance.logs,
            widget=Textarea(attrs={'readonly': True, 'style': 'white-space: pre-wrap;'}),
            required=False,
            label='Logs',
            disabled=True
        )
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
    public = BooleanField(
        widget=HoCheckbox(
            label=Wiki._meta.get_field('public').help_text), required=False, label='')
    show_network_graph = BooleanField(
        widget=HoCheckbox(
            label=Wiki._meta.get_field('show_network_graph').help_text), required=False, label='')
    show_servers = BooleanField(
        widget=HoCheckbox(
            label=Wiki._meta.get_field('show_servers').help_text), required=False, label='')
    show_services = BooleanField(
        widget=HoCheckbox(
            label=Wiki._meta.get_field('show_services').help_text), required=False, label='')
    pinned_servers = ModelMultipleChoiceField(
        queryset=Server.objects.all(),
        required=False,
        label='Pinned Servers',
        help_text='Select servers to pin to the wiki for quick access',
        widget=CheckboxSelectMultiple(attrs={
            'class': 'soft',
        }),
    )
    pinned_services = ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label='Pinned Services',
        help_text='Select services to pin to the wiki for quick access',
        widget=CheckboxSelectMultiple(attrs={
            'class': 'soft',
        }),
    )

    def __init__(self, *args, **kwargs):
        homelab = kwargs.pop('homelab', None)

        super(WikiForm, self).__init__(*args, **kwargs)

        if homelab:
            self.fields['homelab'].initial = homelab
            self.fields['homelab'].disabled = True
            self.fields['pinned_services'].queryset = Service.objects.filter(
                server__homelab=homelab
                )

    class Meta:
        model = Wiki
        fields = '__all__'

class IngressForm(ModelForm):
    enabled = BooleanField(
        widget=HoCheckbox(
            label=Ingress._meta.get_field('enabled').help_text), required=False, label='')
    preserve_host = BooleanField(
        widget=HoCheckbox(
            label=Ingress._meta.get_field('preserve_host').help_text), required=False, label='')
    strip_path_prefix = BooleanField(
        widget=HoCheckbox(
            label=Ingress._meta.get_field('strip_path_prefix').help_text), required=False, label='')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        homelab = kwargs.pop('homelab', None)
        super().__init__(*args, **kwargs)
        
        if user and homelab:
            self.fields['target_service'].queryset = Service.objects.filter(
                server__homelab=homelab, server__user=user
            )
            self.fields['user'].initial = user
            self.fields['user'].disabled = True
            self.fields['homelab'].initial = homelab
            self.fields['homelab'].disabled = True

    class Meta:
        model = Ingress
        fields = '__all__'
