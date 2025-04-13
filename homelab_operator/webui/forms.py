from django.forms import ModelForm
from .models import Server, Service

class ServerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(ServerForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['user'].initial = user
            self.fields['user'].disabled = True
            
    class Meta:
        model = Server
        fields = '__all__'
