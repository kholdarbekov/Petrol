from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, SplitDateTimeField
from django.forms.widgets import TextInput
from .models import Oil, OilTrade, Trade, Car, ProductCheckIn, Product, ProductTrade


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


class ProductCheckInForm(ModelForm):
    def is_valid(self):
        try:
            self.instance.product = Product.objects.get(name=self.data['product'])
        except ObjectDoesNotExist:
            return False
        return super(ProductCheckInForm, self).is_valid()

    class Meta:
        model = ProductCheckIn
        fields = ['checkin_product_quantity', 'date']


class ProductTradeForm(ModelForm):
    dateTime = SplitDateTimeField()

    def clean(self):
        super(ProductTradeForm, self).clean()

    def is_valid(self):
        try:
            self.instance.product = Product.objects.get(name=self.data['product'])
        except ObjectDoesNotExist:
            return False
        return super(ProductTradeForm, self).is_valid()

    class Meta:
        model = ProductTrade
        fields = ['sold_product_quantity', 'dateTime']
