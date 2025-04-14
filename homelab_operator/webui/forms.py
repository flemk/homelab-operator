from django.forms import ModelForm
from django.utils.html import format_html
from .models import Server, Service

class ServerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(ServerForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True

        self.fields['ssh_username'].label = 'SSH Username'
        self.fields['ssh_password'].label = 'SSH Password'
        self.fields['ssh_password'].help_text = format_html('<span class="soft error">SSH credentials are stored in plain text. Use this feature with caution.</span>')
            
    class Meta:
        model = Server
        fields = '__all__'

class ServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Service
        fields = '__all__'
