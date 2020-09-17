from django.contrib import admin
from django.contrib.auth.models import User
from .models import Car, Petrol, Trade, Oil, OilTrade, OilCheckIn
from .forms import OilForm


class MyAdminSite(admin.AdminSite):
    login_template = 'login.html'


admin.site = MyAdminSite()
admin.site.register(User)


class CarAdmin(admin.ModelAdmin):
    def get_trades(self, obj):
        trades = obj.get_trades()
        return '{total_litre} litr, {total_price} so\'m'.format(total_litre=trades['litre'], total_price=trades['total_price'])
    get_trades.short_description = 'Refuelling'

    list_display = ['carNumber', 'model', 'get_trades']


class PetrolAdmin(admin.ModelAdmin):
    list_display = ['brand', 'price']


class TradeAdmin(admin.ModelAdmin):
    list_display = ['car', 'petrol', 'litre', 'price']


class OilAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'RemainingLitres', 'RemainingBottles', 'bottleVolume']
    form = OilForm


class OilTradeAdmin(admin.ModelAdmin):
    def get_dt(self, obj):
        return '{time}'.format(time=obj.dateTime.strftime("%Y.%m.%d"))
    get_dt.short_description = 'Time'

    list_display = ['oil', 'litreSold', 'tradePrice', 'get_dt']

    def delete_queryset(self, request, queryset):
        for obj in queryset:

            obj.oil.RemainingLitres += obj.litreSold

            obj.oil.RemainingBottles = ((obj.oil.RemainingLitres) // obj.oil.bottleVolume)

            obj.oil.save()
        super(OilTradeAdmin, self).delete_queryset(request, queryset)


class OilCheckInAdmin(admin.ModelAdmin):
    list_display = ['oil', 'bottles']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.oil.RemainingBottles -= obj.bottles
            obj.oil.RemainingLitres -= obj.bottles * obj.oil.bottleVolume

            obj.oil.save()

        super(OilCheckInAdmin, self).delete_queryset(request, queryset)


admin.site.register(Car, CarAdmin)
admin.site.register(Petrol, PetrolAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(Oil, OilAdmin)
admin.site.register(OilTrade, OilTradeAdmin)
admin.site.register(OilCheckIn, OilCheckInAdmin)
