from django.forms import ModelForm, SplitDateTimeField
from django.forms.widgets import TextInput
from .models import Oil, OilTrade, Trade


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


class TradeForm(ModelForm):
    tradeDateTime = SplitDateTimeField()

    def __init__(self, *args, **kwargs):
        kwargs['data']._mutable = True
        kwargs['data']['car'] = kwargs['data']['car'].split(' ')[0]
        kwargs['data']._mutable = False
        super(TradeForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(TradeForm, self).clean()

    def is_valid(self):
        return super(TradeForm, self).is_valid()

    class Meta:
        model = Trade
        fields = ['car', 'petrol', 'litre', 'tradeDateTime']
