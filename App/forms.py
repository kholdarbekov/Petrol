from django.forms import ModelForm, SplitDateTimeField
from django.forms.widgets import TextInput
from .models import Oil, OilTrade


class OilForm(ModelForm):
    class Meta:
        model = Oil
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'})
        }


class OilTradeForm(ModelForm):
    dateTime = SplitDateTimeField()

    class Meta:
        model = OilTrade
        fields = ['oil', 'litreSold', 'dateTime']
