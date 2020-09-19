from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

from .views import IndexView, OilsListView, OilCheckInsListView, OilCreateView, OilDeleteView, OilCheckinCreateView, \
    OilCheckinDeleteView, OilTradeCreateView, OilTradeDeleteView, OilTradesListView, CarsListView, CarCreateView, \
    CarDeleteView, TradesListView, TradeCreateView, TradeDeleteView

urlpatterns = [
    path(r'', IndexView.as_view(), name='index'),

    path(r'oils/', OilsListView.as_view(), name='oils_list'),
    path(r'oils/add/', OilCreateView.as_view(), name='oil_add'),
    path(r'oils/delete/', OilDeleteView.as_view(), name='oil_delete'),

    path(r'oils/checkins/', OilCheckInsListView.as_view(), name='oils_checkins'),
    path(r'oils/checkins/add/', OilCheckinCreateView.as_view(), name='oil_checkin_add'),
    path(r'oils/checkins/delete/', OilCheckinDeleteView.as_view(), name='oil_checkin_delete'),

    path(r'oils/trades/', OilTradesListView.as_view(), name='oils_trades'),
    path(r'oils/trades/add/', OilTradeCreateView.as_view(), name='oil_trades_add'),
    path(r'oils/trades/delete/', OilTradeDeleteView.as_view(), name='oil_trades_delete'),

    path(r'petrol/cars/', CarsListView.as_view(), name='cars_list'),
    path(r'petrol/cars/add/', CarCreateView.as_view(), name='car_add'),
    path(r'petrol/cars/delete/', CarDeleteView.as_view(), name='car_delete'),

    path(r'petrol/trades/', TradesListView.as_view(), name='trades_list'),
    path(r'petrol/trades/add/', TradeCreateView.as_view(), name='trade_add'),
    path(r'petrol/trades/delete/', TradeDeleteView.as_view(), name='trade_delete'),
]
