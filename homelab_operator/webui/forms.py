'''Forms for the web UI of the homelab operator project.'''

from django.forms import ModelForm, DateTimeInput, BooleanField, CharField, Textarea, \
    ModelMultipleChoiceField, CheckboxSelectMultiple, ChoiceField, Select, ValidationError, \
    DateInput
from .models import Server, Service, Network, WOLSchedule, ShutdownURLConfiguration, Homelab, \
    Wiki, UserProfile, Ingress, MaintenancePlan, MaintenanceReport
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

class MaintenancePlanForm(ModelForm):
    '''Form for creating and updating MaintenancePlan instances.'''
    instance_choice = ChoiceField(
        label='Select Entity',
        widget=Select()
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        homelab = kwargs.pop('homelab', None)
        
        super(MaintenancePlanForm, self).__init__(*args, **kwargs)

        # Build choices dynamically
        choices = [('', 'Select...')]

        if user:
            self.fields['assignee'].initial = user.profile
            self.fields['assignee'].disabled = True

            if homelab:
                servers = Server.objects.filter(user=user, homelab=homelab)
                services = Service.objects.filter(server__user=user, server__homelab=homelab)
                networks = Network.objects.filter(user=user, homelab=homelab)
                ingresses = Ingress.objects.filter(homelab=homelab, user=user)
            else:
                servers = Server.objects.filter(user=user)
                services = Service.objects.filter(server__user=user)
                networks = Network.objects.filter(user=user)
                ingresses = Ingress.objects.filter(user=user)
            homelabs = Homelab.objects.filter(user=user, id=homelab.id)

            # Add homelab choices
            homelab_choices = [(f'homelab_{homelab.id}', f'{homelab.name}') for homelab in homelabs]
            if homelab_choices:
                choices.append(('Homelabs', homelab_choices))

            # Add server choices
            server_choices = [(f'server_{s.id}', f'{s.name}') for s in servers]
            if server_choices:
                choices.append(('Servers', server_choices))

            # Add service choices
            service_choices = [(f'service_{s.id}', f'{s.name} ({s.server.name})') for s in services]
            if service_choices:
                choices.append(('Services', service_choices))
            
            # Add network choices
            network_choices = [(f'network_{network.id}', f'{network.name}') for network in networks]
            if network_choices:
                choices.append(('Networks', network_choices))
            
            # Add ingress choices
            ingress_choices = [(f'ingress_{ingress.id}', f'{ingress.name}') for ingress in ingresses]
            if ingress_choices:
                choices.append(('Ingresses', ingress_choices))

        self.fields['instance_choice'].choices = choices

        # Set initial value if editing
        if self.instance and self.instance.pk:
            self.fields['instance_choice'].initial = f'{self.instance.content_type.model}_{self.instance.object_id}'

    def clean_instance_choice(self):
        choice = self.cleaned_data.get('instance_choice')
        if not choice:
            raise ValidationError('Please select an entity.')

        choice_type, choice_id = choice.split('_', 1)
        try:
            if choice_type == 'server':
                return Server.objects.get(id=choice_id)
            elif choice_type == 'service':
                return Service.objects.get(id=choice_id)
            elif choice_type == 'homelab':
                return Homelab.objects.get(id=choice_id)
            elif choice_type == 'network':
                return Network.objects.get(id=choice_id)
            elif choice_type == 'ingress':
                return Ingress.objects.get(id=choice_id)
        except (Server.DoesNotExist, Service.DoesNotExist):
            raise ValidationError('Invalid selection.')

        raise ValidationError('Invalid choice format.')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.instance = self.cleaned_data.get('instance_choice')

        if commit:
            instance.save()
        return instance

    class Meta:
        model = MaintenancePlan
        exclude = ['content_type', 'object_id']
        widgets = {
            'scheduled_date': DateInput(attrs={'type': 'date'}),
        }

class MaintenanceReportForm(ModelForm):
    '''Form for creating and updating MaintenanceReport instances.'''
    def __init__(self, *args, **kwargs):
        certifier = kwargs.pop('certifier', None)
        maintenance_plan = kwargs.pop('maintenance_plan', None)
        immutable = kwargs.pop('immutable', False)

        super(MaintenanceReportForm, self).__init__(*args, **kwargs)

        if certifier:
            self.fields['certifier'].initial = certifier
            self.fields['certifier'].disabled = True
        
        if maintenance_plan:
            self.fields['maintenance_plan'].initial = maintenance_plan
            self.fields['maintenance_plan'].disabled = True

        if immutable:
            for field in self.fields:
                self.fields[field].disabled = True
            self.fields['notes'].widget = Textarea(attrs={'rows': 5, 'readonly': True})

    class Meta:
        model = MaintenanceReport
        fields = '__all__'
        widgets = {
            'report_date': DateInput(attrs={'type': 'date'}),
            'content': Textarea(attrs={'rows': 5}),
        }
