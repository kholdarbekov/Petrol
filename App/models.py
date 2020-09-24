from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models


class CarModel(models.Model):
    name = models.CharField(primary_key=True, max_length=31)
    description = models.TextField(blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    carNumber = models.CharField(primary_key=True, max_length=8)
    model = models.ForeignKey(CarModel, related_name='cars', on_delete=models.CASCADE)
    used_bonuses = models.PositiveSmallIntegerField(default=0)
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    def get_trades(self):
        trades = {'litre': 0, 'total_price': 0}
        for t in self.trades.all():
            trades['litre'] += t.litre
            trades['total_price'] += t.price
        return trades

    def __str__(self):
        return '{carNumber} {model}'.format(carNumber=self.carNumber, model=self.model)

    class Meta:
        verbose_name = 'Машина'
        verbose_name_plural = 'Машины'


class Petrol(models.Model):  # Benzin
    brand = models.CharField(primary_key=True, max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.brand

    class Meta:
        verbose_name = verbose_name_plural = 'Бензин'


class Trade(models.Model):  # for Petrol
    car = models.ForeignKey(Car, related_name='trades', on_delete=models.CASCADE)
    petrol = models.ForeignKey(Petrol, related_name='trades', on_delete=models.CASCADE)
    litre = models.PositiveSmallIntegerField()
    tradeDateTime = models.DateTimeField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True)

    def __str__(self):
        return '{car} {petrol} {litre} litr {time}'.format(car=self.car.carNumber, petrol=self.petrol.brand, litre=self.litre, time=self.tradeDateTime.strftime("%Y-%m-%d %H:%M"))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            self.price = self.litre * self.petrol.price
        except ObjectDoesNotExist:
            self.price = 0
        except MultipleObjectsReturned:
            self.price = 0

        super(Trade, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = verbose_name_plural = 'Refuelling'


class Oil(models.Model):
    name = models.CharField(primary_key=True, max_length=63)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    RemainingLitres = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    RemainingBottles = models.PositiveIntegerField(default=0)
    bottleVolume = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    color = models.CharField(null=True, blank=True, max_length=7)
    created = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Oil'
        verbose_name_plural = 'Oils'


class OilTrade(models.Model):
    oil = models.ForeignKey(Oil, related_name='trades', on_delete=models.CASCADE)
    litreSold = models.DecimalField(decimal_places=1, max_digits=4)
    tradePrice = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    dateTime = models.DateTimeField(blank=True)

    def __str__(self):
        return '{oil} dan {litre} litr {time}'.format(oil=self.oil, litre=self.litreSold, time=self.dateTime.strftime("%Y-%m-%d %H:%M"))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            self.tradePrice = self.oil.price * self.litreSold

            openedOilLitre = self.oil.RemainingLitres % self.oil.bottleVolume
            if self.oil.RemainingLitres < self.litreSold:
                return

            self.oil.RemainingLitres -= self.litreSold

            if openedOilLitre < self.litreSold:  # new bottle is opened
                if self.litreSold - openedOilLitre == self.oil.bottleVolume:
                    self.oil.RemainingBottles -= 1
                else:
                    self.oil.RemainingBottles -= ((self.litreSold - openedOilLitre) // self.oil.bottleVolume) + 1

            self.oil.save()

        except ObjectDoesNotExist:
            self.tradePrice = 0

        except MultipleObjectsReturned:
            self.tradePrice = 0
        super(OilTrade, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = 'Oil Trade'
        verbose_name_plural = 'Oil Trades'


class OilCheckIn(models.Model):
    oil = models.ForeignKey(Oil, related_name='checkins', on_delete=models.CASCADE)
    bottles = models.PositiveIntegerField(default=0)
    date = models.DateField(blank=True)

    def __str__(self):
        return '{oil} dan {bottles} ta keldi'.format(oil=self.oil, bottles=self.bottles)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.oil.RemainingBottles += self.bottles
        self.oil.RemainingLitres += self.bottles * self.oil.bottleVolume
        self.oil.save()

        super(OilCheckIn, self).save(force_insert, force_update, using, update_fields)