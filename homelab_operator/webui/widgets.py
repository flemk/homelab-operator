from django.forms.widgets import CheckboxInput

class HoCheckbox(CheckboxInput):
    template_name = 'widgets/checkbox.html'

    def __init__(self, *args, label=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['label'] = self.label
        return context
