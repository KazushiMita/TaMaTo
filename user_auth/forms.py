from django import forms
from .models import RetweetQueue

class RetweetQueueForm(forms.ModelForm):
    class Meta:
        model = RetweetQueue
        fields = ('status_id', )
    

class RetweetQueueUpdateForm(forms.ModelForm):
    class Meta:
        model = RetweetQueue
        fields = (
            'running',
        )
