from decimal import Decimal, InvalidOperation

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

    def clean(self):
        cd = super(OilTradeForm, self).clean()
        if 'oil' not in cd:
            self.errors.pop('oil')  # Removing English error message and then adding Uzbek error message
            if self.data['oil'] == '':
                self.add_error('oil', 'Yog\' Nomi bo\'sh bo\'lmasligi kerak')
            else:
                self.add_error('oil', 'Siz kiritgan "' + self.data['oil'] + '" yog\' topilmadi')
            return cd

        if 'litreSold' not in cd:
            self.errors.pop('litreSold')  # Removing English error message and then adding Uzbek error message
            if self.data['litreSold'] == '':
                self.add_error('litreSold', 'Sotilgan Litr bo\'sh bo\'lmasligi kerak')
            else:
                self.add_error('litreSold', 'To\'g\'ri formatda son kiriting')
            return cd
        else:
            litre_sold = Decimal(cd['litreSold'])
            if litre_sold <= 0:
                self.add_error('litreSold', 'Sotilgan litr 0 dan katta bo\'lishi kerak')
                return cd
            oil = Oil.objects.get(name=cd['oil'])
            if oil.RemainingLitres < litre_sold:
                self.add_error('litreSold', 'Kiritilgan litr qolgan yog\' miqdoridan oshib ketdi')

        return cd

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
        cd = super(ProductTradeForm, self).clean()
        try:
            self.instance.product = Product.objects.get(name=self.data['product'])
        except ObjectDoesNotExist:
            self.add_error('sold_product_quantity', 'Product topilmadi')
            return cd

        if self.instance.product.remaining_quantity < Decimal(self.data['sold_product_quantity']):
            self.add_error('sold_product_quantity', 'Sotilayotgan product qolgan product sonidan ortiq')
            return cd

    def is_valid(self):
        return super(ProductTradeForm, self).is_valid()

    class Meta:
        model = ProductTrade
        fields = ['sold_product_quantity', 'dateTime']
