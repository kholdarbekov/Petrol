import re
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, SplitDateTimeField
from django.forms.widgets import TextInput
from django.forms.utils import ErrorList
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
                self.add_error('litreSold', 'Sotilgan litr sonini to\'g\'ri formatda kiriting')
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
        cd = super(TradeForm, self).clean()
        if 'car' not in cd:
            self.errors.pop('car')  # Removing English error message and then adding Uzbek error message
            if self.data['car'] == '':
                self.add_error('car', 'Mashina raqami bo\'sh bo\'lmasligi kerak')
            else:
                self.add_error('car', 'Siz kiritgan "' + self.data['car'] + '" mashina topilmadi')
            return cd

        if 'petrol' not in cd:
            self.errors.pop('petrol')  # Removing English error message and then adding Uzbek error message
            if self.data['petrol'] == '':
                self.add_error('petrol', 'Benzin nomi bo\'sh bo\'lmasligi kerak')
            else:
                self.add_error('petrol', 'Siz kiritgan "' + self.data['petrol'] + '" benzini topilmadi')
            return cd

        if 'litre' not in cd:
            self.errors.pop('litre')  # Removing English error message and then adding Uzbek error message
            if self.data['litre'] == '':
                self.add_error('litre', 'Sotilgan Litr bo\'sh bo\'lmasligi kerak')
            else:
                self.add_error('litre', 'Sotilgan Litrni to\'g\'ri formatda kiriting')
            return cd
        else:
            litre = Decimal(cd['litre'])
            if litre <= 0:
                self.add_error('litre', 'Sotilgan litr 0 dan katta bo\'lishi kerak')
                return cd
            if litre > settings.PETROL_BONUS_LIMIT:
                self.add_error('litre', 'Sotilgan Litr miqdori juda katta')
                return cd

        return cd

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


class CarForm(ModelForm):

    def clean(self):
        cd = super(CarForm, self).clean()
        correct_pattern = re.compile(r"\d{2}[0-9A-Za-z]\d{2}[0-9A-Za-z][A-Za-z]{2}")
        cyrillic_letters = re.compile(r"[а-яА-Я]+")
        if 'carNumber' not in cd:
            self.errors.pop('carNumber')  # Removing English error message and then adding Uzbek error message
            if self.data['carNumber'] == '':
                self.add_error('carNumber', 'Mashina raqami bo\'sh bo\'lmasligi kerak')
                return cd
            else:
                carNumber = self.data['carNumber'].replace('-', '').upper()
                m = correct_pattern.match(carNumber)
                if m:
                    numbers = re.sub(r'[a-zA-Z]+', '', m[0])
                    if len(numbers[2:]) != 3:
                        self.add_error('carNumber', 'Mashina raqami (%s) noto\'g\'ri kiritildi, tekshirib qaytadan urinib koring' % carNumber)
                        return cd

                    try:
                        if Car.objects.get(carNumber=carNumber):
                            self.add_error('carNumber', 'Bunaqa raqamli (%s) mashina registratsiyadan o\'tgan' % carNumber)
                            return cd
                    except ObjectDoesNotExist:
                        pass

                    cyrillic_m = cyrillic_letters.match(carNumber)
                    if cyrillic_m:
                        self.add_error('carNumber', 'Mashina raqamini kirilcha harflarsiz kirgazing. Faqat Lotin harflari va sonlar mumkin')
                        return cd

                    cd['carNumber'] = carNumber
                else:
                    self.add_error('carNumber', 'Siz kiritgan "' + self.data['carNumber'] + '" mashina raqami xato')
                    return cd
        else:
            m = correct_pattern.match(cd['carNumber'])
            if not m:
                self.add_error('carNumber', 'Mashina raqamini to\'g\'ri formatda kiriting (Masalan: 70-A100AA yoki 70-100AAA)')
                return cd
            else:
                numbers = re.sub(r'[a-zA-Z]+', '', cd['carNumber'])
                if len(numbers[2:]) != 3:
                    self.add_error('carNumber', 'Mashina raqami (%s) noto\'g\'ri kiritildi, tekshirib qaytadan urinib koring' % cd['carNumber'])
                    return cd

                try:
                    if Car.objects.get(carNumber=cd['carNumber']):
                        self.add_error('carNumber', 'Bunaqa raqamli (%s) mashina registratsiyadan o\'tgan' % cd['carNumber'])
                        return cd
                except ObjectDoesNotExist:
                    pass

            cyrillic_m = cyrillic_letters.match(cd['carNumber'])
            if cyrillic_m:
                self.add_error('carNumber', 'Mashina raqamini kirilcha harflarsiz kirgazing. Faqat Lotin harflari va sonlar mumkin')
                return cd

            cd['carNumber'] = cd['carNumber'].upper()

        if 'model' not in cd:
            self.errors.pop('model')  # Removing English error message and then adding Uzbek error message
            if self.data['model'] == '':
                self.add_error('model', 'Model nomi bo\'sh bo\'lmasligi kerak')
            else:
                m = cyrillic_letters.match(self.data['model'])
                if m:
                    self.add_error('model', 'Model nomini kirilcha harflarsiz kirgazing. Faqat Lotin harflari mumkin')
                    return cd
                self.add_error('model', 'Siz kiritgan "' + self.data['model'] + '" model topilmadi')
            return cd

        return cd

    class Meta:
        model = Car
        fields = ['carNumber', 'model']


class SuccessList(ErrorList):
    def __init__(self):
        super().__init__()
        self.error_class = 'successlist'
