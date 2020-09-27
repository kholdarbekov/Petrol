from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class Config(models.Model):
    petrol_bonus_limit = models.PositiveSmallIntegerField(default=500)

    def __str__(self):
        return '%d' % self.petrol_bonus_limit

    def clean(self):
        if not self.pk and Config.objects.exists():
            # if you'll not check for self.pk
            # then error will also raised in update of exists model
            raise ValidationError('There can be only one Config instance')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        settings.PETROL_BONUS_LIMIT = self.petrol_bonus_limit
        return super(Config, self).save(force_insert, force_update, using, update_fields)


class Member(User):
    MANAGER = 'manager'
    STAFF = 'staff'
    OIL = 'oil'
    PETROL = 'petrol'
    GENERAL = 'general'

    class Meta:
        proxy = True

    @property
    def is_general_staff(self):
        if self:
            return self.first_name.lower().strip() == self.STAFF and self.last_name.lower().strip() == self.GENERAL
        else:
            return False

    @property
    def is_oil_staff(self):
        if self:
            return self.first_name.lower().strip() == self.STAFF and self.last_name.lower().strip() == self.OIL
        else:
            return False

    @property
    def is_petrol_staff(self):
        if self:
            return self.first_name.lower().strip() == self.STAFF and self.last_name.lower().strip() == self.PETROL
        else:
            return False

    @property
    def is_manager(self):
        if self:
            return self.first_name.lower().strip() == self.MANAGER
        else:
            return False

    @property
    def is_user_staff(self):
        if self:
            return self.first_name.lower().strip() == self.STAFF
        else:
            return False


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
    total_bought_litres = models.PositiveSmallIntegerField(default=0)
    total_bought_price = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    total_litres_after_bonus = models.PositiveSmallIntegerField(default=0)
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    @property
    def get_litres_after_bonuses(self):
        return self.total_bought_litres - self.used_bonuses * settings.PETROL_BONUS_LIMIT

    def __str__(self):
        return '{carNumber} {model}'.format(carNumber=self.carNumber, model=self.model)


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
        if self.litre <= settings.PETROL_BONUS_LIMIT:
            try:
                self.price = self.litre * self.petrol.price
                self.car.total_bought_litres += self.litre
                self.car.total_litres_after_bonus += self.litre
                self.car.total_bought_price += self.price
                self.car.save()
            except ObjectDoesNotExist:
                self.price = 0
            except MultipleObjectsReturned:
                self.price = 0

            super(Trade, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.car.total_bought_litres -= self.litre
        if self.litre > self.car.total_litres_after_bonus:
            self.car.total_litres_after_bonus = settings.PETROL_BONUS_LIMIT + self.car.total_litres_after_bonus - self.litre
            self.car.used_bonuses -= 1
        else:
            self.car.total_litres_after_bonus -= self.litre
        self.car.total_bought_price -= self.price
        self.car.save()
        super(Trade, self).delete(using, keep_parents)

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

    def delete(self, using=None, keep_parents=False):
        self.oil.RemainingLitres += self.litreSold
        self.oil.RemainingBottles = self.oil.RemainingLitres // self.oil.bottleVolume
        self.oil.save()
        super(OilTrade, self).delete(using, keep_parents)

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

    def delete(self, using=None, keep_parents=False):
        self.oil.RemainingBottles -= self.bottles
        self.oil.RemainingLitres -= self.bottles * self.oil.bottleVolume
        self.oil.save()
        super(OilCheckIn, self).delete(using, keep_parents)
