from django.contrib import admin
from .models import CarModel, Car, Petrol, Trade, Oil, OilTrade, OilCheckIn, Config
from .forms import OilForm


admin.site.login_template = 'login.html'
admin.site.site_header = 'Petrol'
admin.site.site_title = 'Petrol'


class ConfigAdmin(admin.ModelAdmin):
    list_display = ['petrol_bonus_limit']


class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created']
    list_per_page = 50
    search_fields = ['name']
    list_filter = ['name']
    date_hierarchy = 'created'


class CarAdmin(admin.ModelAdmin):
    list_display = ['carNumber', 'model', 'used_bonuses', 'total_bought_litres', 'total_bought_price', 'created', 'last_updated']
    list_per_page = 30
    search_fields = ['carNumber', 'model__name']
    list_filter = ['model']
    date_hierarchy = 'created'


class PetrolAdmin(admin.ModelAdmin):
    list_display = ['brand', 'price']
    list_per_page = 10
    search_fields = ['brand']
    list_filter = ['brand']


class TradeAdmin(admin.ModelAdmin):
    list_display = ['car', 'petrol', 'litre', 'price', 'tradeDateTime']
    list_per_page = 30
    search_fields = ['car__carNumber', 'car__model__name', 'petrol__brand', 'litre']
    list_filter = ['petrol']
    date_hierarchy = 'tradeDateTime'


class OilAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'RemainingLitres', 'RemainingBottles', 'bottleVolume']
    form = OilForm
    list_per_page = 30
    search_fields = ['name']
    list_filter = ['bottleVolume']
    date_hierarchy = 'created'


class OilTradeAdmin(admin.ModelAdmin):
    def get_dt(self, obj):
        return '{time}'.format(time=obj.dateTime.strftime("%Y.%m.%d"))
    get_dt.short_description = 'Time'

    list_display = ['oil', 'litreSold', 'tradePrice', 'get_dt']
    list_per_page = 30
    search_fields = ['oil__name']
    list_filter = ['oil']
    date_hierarchy = 'dateTime'

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.oil.RemainingLitres += obj.litreSold
            obj.oil.RemainingBottles = ((obj.oil.RemainingLitres) // obj.oil.bottleVolume)
            obj.oil.save()
        super(OilTradeAdmin, self).delete_queryset(request, queryset)


class OilCheckInAdmin(admin.ModelAdmin):
    list_display = ['oil', 'bottles']
    list_per_page = 30
    search_fields = ['oil__name']
    list_filter = ['oil']
    date_hierarchy = 'date'

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.oil.RemainingBottles -= obj.bottles
            obj.oil.RemainingLitres -= obj.bottles * obj.oil.bottleVolume

            obj.oil.save()

        super(OilCheckInAdmin, self).delete_queryset(request, queryset)


admin.site.register(Config, ConfigAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Petrol, PetrolAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(Oil, OilAdmin)
admin.site.register(OilTrade, OilTradeAdmin)
admin.site.register(OilCheckIn, OilCheckInAdmin)
