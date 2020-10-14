from django.conf.urls import url
from django.urls import path, re_path

from .views import IndexView, OilsListView, OilCheckInsListView, OilCreateView, OilDeleteView, OilCheckinCreateView, \
    OilCheckinDeleteView, OilTradeCreateView, OilTradeDeleteView, OilTradesListView, CarsListView, CarCreateView, \
    CarDeleteView, TradesListView, TradeCreateView, TradeDeleteView, OilUpdateView, CarBonusUpdateView, \
    ProductsListView, ProductCreateView, ProductDeleteView, ProductUpdateView, ProductCheckInsListView, \
    ProductCheckinCreateView, ProductCheckinDeleteView, ProductTradesListView, ProductTradeCreateView, \
    ProductTradeDeleteView, CarBonusDetail

urlpatterns = [
    path(r'dashboard/oil/', IndexView.as_view(), name='index'),

    path(r'oils/', OilsListView.as_view(), name='oils_list'),
    path(r'oils/add/', OilCreateView.as_view(), name='oil_add'),
    path(r'oils/delete/', OilDeleteView.as_view(), name='oil_delete'),
    path(r'oils/update/', OilUpdateView.as_view(), name='oil_update'),

    path(r'oils/checkins/', OilCheckInsListView.as_view(), name='oils_checkins'),
    path(r'oils/checkins/add/', OilCheckinCreateView.as_view(), name='oil_checkin_add'),
    path(r'oils/checkins/delete/', OilCheckinDeleteView.as_view(), name='oil_checkin_delete'),

    path(r'oils/trades/', OilTradesListView.as_view(), name='oils_trades'),
    path(r'oils/trades/add/', OilTradeCreateView.as_view(), name='oil_trades_add'),
    path(r'oils/trades/delete/', OilTradeDeleteView.as_view(), name='oil_trades_delete'),

    path(r'', CarsListView.as_view(), name='cars_list'),
    path(r'petrol/cars/add/', CarCreateView.as_view(), name='car_add'),
    path(r'petrol/cars/delete/', CarDeleteView.as_view(), name='car_delete'),
    path(r'petrol/cars/bonus/', CarBonusUpdateView.as_view(), name='car_bonus'),
    path(r'petrol/cars/bonus/detail/', CarBonusDetail.as_view(), name='car_bonus_details'),

    path(r'petrol/trades/', TradesListView.as_view(), name='trades_list'),
    path(r'petrol/trades/add/', TradeCreateView.as_view(), name='trade_add'),
    path(r'petrol/trades/delete/', TradeDeleteView.as_view(), name='trade_delete'),

    re_path(r'^products/(?P<slug>[-\w]+)/$', ProductsListView.as_view(), name='products_list'),
    re_path(r'^products/(?P<slug>[-\w]+)/add/$', ProductCreateView.as_view(), name='product_add'),
    re_path(r'^products/(?P<slug>[-\w]+)/delete/$', ProductDeleteView.as_view(), name='product_delete'),
    re_path(r'^products/(?P<slug>[-\w]+)/update/$', ProductUpdateView.as_view(), name='product_update'),

    re_path(r'^products/(?P<slug>[-\w]+)/checkins/$', ProductCheckInsListView.as_view(), name='products_checkins'),
    re_path(r'^products/(?P<slug>[-\w]+)/checkins/add/$', ProductCheckinCreateView.as_view(), name='product_checkin_add'),
    re_path(r'^products/(?P<slug>[-\w]+)/checkins/delete/$', ProductCheckinDeleteView.as_view(), name='product_checkin_delete'),

    re_path(r'^products/(?P<slug>[-\w]+)/trades/$', ProductTradesListView.as_view(), name='products_trades'),
    re_path(r'^products/(?P<slug>[-\w]+)/trades/add/$', ProductTradeCreateView.as_view(), name='product_trades_add'),
    re_path(r'^products/(?P<slug>[-\w]+)/trades/delete/$', ProductTradeDeleteView.as_view(), name='product_trades_delete'),
]
