from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.conf import settings
from django.forms.utils import ErrorList

from .models import OilTrade, OilCheckIn, Oil, Car, Trade, CarModel, Petrol, Member, ProductCategory, Product, ProductTrade, ProductCheckIn
from .forms import OilTradeForm, TradeForm, ProductCheckInForm, ProductTradeForm, CarForm, SuccessList


class ConfiguredListView(ListView):
    def __init__(self):
        self.member = None
        super(ConfiguredListView, self).__init__()

    def setup(self, request, *args, **kwargs):
        super(ConfiguredListView, self).setup(request, *args, **kwargs)
        try:
            self.member = Member.objects.get(username=self.request.user.username)
        except ObjectDoesNotExist:
            self.member = request.user

    # set user and product_categories to context
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConfiguredListView, self).get_context_data(**kwargs)
        context['user'] = self.member
        context['product_categories'] = ProductCategory.objects.exclude(slug='default')

        return context


class IndexView(TemplateView):
    template_name = 'index.html'
    oil_trades_page = reverse_lazy('oils_trades')
    petrol_cars_list_page = reverse_lazy('cars_list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        member = Member.objects.get(username=self.request.user.username)
        if not member.is_manager:  # if member is STAFF
            if member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if member.is_oil_staff:
                return redirect(self.oil_trades_page)

        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        currentTime = timezone.localtime(timezone.now())
        last_year_range = [(currentTime - timezone.timedelta(days=356)), currentTime]

        context = super(IndexView, self).get_context_data(**kwargs)

        context['user'] = Member.objects.get(username=self.request.user.username)

        context['oilTrades'] = {}

        context['fromTradeTime'] = ''
        context['toTradeTime'] = ''

        context['oils'] = {}

        context['oilCheckIns'] = {}

        context['last12MonthSale'] = {}
        context['last12MonthSale']['Jan'] = 0
        context['last12MonthSale']['Feb'] = 0
        context['last12MonthSale']['Mar'] = 0
        context['last12MonthSale']['Apr'] = 0
        context['last12MonthSale']['May'] = 0
        context['last12MonthSale']['Jun'] = 0
        context['last12MonthSale']['Jul'] = 0
        context['last12MonthSale']['Aug'] = 0
        context['last12MonthSale']['Sep'] = 0
        context['last12MonthSale']['Oct'] = 0
        context['last12MonthSale']['Nov'] = 0
        context['last12MonthSale']['Dec'] = 0

        context['totalRemaining'] = 0

        context['totalRemainingPrice'] = 0

        context['totalSold'] = 0

        for o in Oil.objects.all():
            context['oilTrades'][o.name] = []
            context['oilTrades'][o.name] += o.trades.filter(dateTime__range=last_year_range).order_by('dateTime').values('oil', 'litreSold', 'tradePrice', 'dateTime')

            context['oils'][o.name] = o

            context['totalRemaining'] += o.RemainingLitres

            context['totalRemainingPrice'] += o.RemainingLitres * o.price

        i = 0
        lastDateTime = ''
        for t in OilTrade.objects.filter(dateTime__range=last_year_range).order_by('-dateTime'):
            if i == 0:
                context['toTradeTime'] = (t.dateTime + timezone.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
            i += 1
            lastDateTime = (t.dateTime - timezone.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")

            context['last12MonthSale'][t.dateTime.strftime("%b")] += t.tradePrice
            context['totalSold'] += t.litreSold
        context['fromTradeTime'] = lastDateTime

        for c in OilCheckIn.objects.filter(date__range=last_year_range).order_by('-date'):
            context['oilCheckIns'][c.id] = c

        context['product_categories'] = ProductCategory.objects.exclude(slug='default')

        return context


class OilsListView(ConfiguredListView):
    model = Oil
    context_object_name = 'oils'
    template_name = 'oilsList.html'
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)


class OilCreateView(CreateView):
    model = Oil
    fields = ['name', 'price', 'RemainingLitres', 'RemainingBottles', 'bottleVolume', 'color']
    success_url = reverse_lazy('oils_list')
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.member
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OilDeleteView(DeleteView):
    model = Oil
    success_url = reverse_lazy('oils_list')
    http_method_names = ['post', ]
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Oil, name=self.request.POST['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponse(success_url)


class OilUpdateView(UpdateView):
    model = Oil
    fields = ['name', 'price', 'RemainingLitres', 'RemainingBottles', 'bottleVolume', 'color']
    success_url = reverse_lazy('oils_list')
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Oil, name=self.request.POST['oldName'])

    def form_valid(self, form):
        form.instance.name = self.request.POST['oldName']
        return super().form_valid(form)


class OilCheckInsListView(ConfiguredListView):
    model = OilCheckIn
    context_object_name = 'oilCheckIns'
    template_name = 'oilCheckIns.html'
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['oils'] = Oil.objects.all()
        return context


class OilCheckinCreateView(CreateView):
    model = OilCheckIn
    fields = ['oil', 'bottles', 'date']
    success_url = reverse_lazy('oils_checkins')
    template_name = 'oilCheckIns.html'
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.member
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OilCheckinDeleteView(DeleteView):
    model = OilCheckIn
    success_url = reverse_lazy('oils_checkins')
    http_method_names = ['post', ]
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(OilCheckIn, pk=self.request.POST['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponse(success_url)


class OilTradesListView(ConfiguredListView):
    model = OilTrade
    context_object_name = 'oilTrades'
    template_name = 'oilsTrades.html'
    petrol_cars_list_page = reverse_lazy('cars_list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if self.member.is_petrol_staff:
            return redirect(self.petrol_cars_list_page)
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['oils'] = Oil.objects.all()
        return context


class OilTradeCreateView(CreateView):
    model = OilTrade
    # fields = ['oil', 'litreSold', 'dateTime']
    success_url = reverse_lazy('oils_trades')
    template_name = 'oilsTrades.html'
    form_class = OilTradeForm
    petrol_cars_list_page = reverse_lazy('cars_list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if self.member.is_petrol_staff:
            return redirect(self.petrol_cars_list_page)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.member
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, error in form.errors.items():
            messages.error(self.request, error)

        return redirect(self.success_url)


class OilTradeDeleteView(DeleteView):
    model = OilTrade
    success_url = reverse_lazy('oils_trades')
    http_method_names = ['post', ]
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(OilTrade, pk=self.request.POST['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponse(success_url)


class CarsListView(ConfiguredListView):
    model = Car
    context_object_name = 'cars'
    template_name = 'carsList.html'
    oil_trades_page = reverse_lazy('oils_trades')

    def dispatch(self, *args, **kwargs):
        # if not self.member.is_manager:  # if member is STAFF
        #     if self.member.is_oil_staff:
        #         return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carModels'] = CarModel.objects.all()
        context['bonus_limit'] = settings.PETROL_BONUS_LIMIT
        return context


def get_default_member():
    return Member.objects.get_or_create(username='default')[0]


class CarCreateView(CreateView):
    model = Car
    # ields = ['carNumber', 'model']
    success_url = reverse_lazy('cars_list')
    template_name = 'carsList.html'
    oil_trades_page = reverse_lazy('oils_trades')
    form_class = CarForm

    def dispatch(self, *args, **kwargs):
        try:
            self.member = Member.objects.get(username=self.request.user.username)
        except ObjectDoesNotExist:
            self.member = get_default_member()
        # if not self.member.is_manager:  # if member is STAFF
        #     if self.member.is_oil_staff:
        #         return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.member

        if self.request.session.get('car_create_count', False):
            if self.request.session.get('car_create_count') <= settings.PETROL_DAILY_CAR_CREATE_LIMIT:
                self.request.session['car_create_count'] += 1
        else:
            self.request.session['car_create_count'] = 1
            self.request.session.set_expiry(86400)  # 1 day

        if self.request.session.get('car_create_count', 1) > settings.PETROL_DAILY_CAR_CREATE_LIMIT:
            car_create_limit_error = ErrorList()
            car_create_limit_error.data.append('1 kunda maximum %d ta mashina registratsiya qila olasiz' % settings.PETROL_DAILY_CAR_CREATE_LIMIT)
            messages.error(self.request, car_create_limit_error, 'car_create')
            return redirect(self.success_url)
        else:
            success_message = SuccessList()
            success_message.data.append(form.instance.carNumber + ' Registratsiyadan o\'tkazildi')
            messages.success(self.request, success_message, 'car_create')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, error in form.errors.items():
            messages.error(self.request, error)

        return redirect(self.success_url)


class CarDeleteView(DeleteView):
    model = Car
    success_url = reverse_lazy('cars_list')
    http_method_names = ['post', ]
    oil_trades_page = reverse_lazy('oils_trades')
    petrol_cars_list_page = reverse_lazy('cars_list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Car, carNumber=self.request.POST['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponse(success_url)


class CarBonusUpdateView(UpdateView):
    model = Car
    fields = ['carNumber']
    success_url = reverse_lazy('cars_list')
    template_name = 'carsList.html'
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Car, carNumber=self.request.POST['carNumber'])

    def form_valid(self, form):
        if form.instance.total_litres_after_bonus >= settings.PETROL_BONUS_LIMIT:
            form.instance.used_bonuses += 1
            form.instance.total_litres_after_bonus -= settings.PETROL_BONUS_LIMIT
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class CarBonusDetail(DetailView):
    model = Car
    context_object_name = 'car'
    template_name = 'carsList.html'
    success_url = reverse_lazy('cars_list')

    def post(self, request, *args, **kwargs):
        if self.request.session.get('car_bonus_check_count', False):
            if self.request.session.get('car_bonus_check_count', 1) <= settings.PETROL_DAILY_CAR_BONUS_CHECK_LIMIT:
                self.request.session['car_bonus_check_count'] += 1
        else:
            self.request.session['car_bonus_check_count'] = 1
            self.request.session.set_expiry(86400)  # 1 day

        if self.request.session.get('car_bonus_check_count', 1) > settings.PETROL_DAILY_CAR_BONUS_CHECK_LIMIT:
            car_create_limit_error = ErrorList()
            car_create_limit_error.data.append('1 kunda maximum %d marta avtomobil bonusini tekshira olasiz' % settings.PETROL_DAILY_CAR_BONUS_CHECK_LIMIT)
            messages.error(self.request, car_create_limit_error, 'bonus_details')
        else:
            self.object = self.get_object()
            if self.object:
                success_message = SuccessList()
                success_message.data.append(
                    '{car} avtomobili {litre_after_bonus} L benzin sotib olgan'.format(car=self.object,
                                                                                       litre_after_bonus=self.object.total_litres_after_bonus))
                messages.success(self.request, success_message, 'bonus_details')
            else:
                car_create_limit_error = ErrorList()
                car_create_limit_error.data.append('Siz kiritgan avtomobil topilmadi')
                messages.error(self.request, car_create_limit_error, 'bonus_details')

        return redirect(self.success_url)

    def get_object(self, queryset=None):
        try:
            carNum = self.request.POST['carNumber']
            if carNum and type(carNum) == str:
                carNum = carNum.replace('-', '').upper()
            else:
                carNum = ''
            obj = Car.objects.get(carNumber=carNum)
        except ObjectDoesNotExist:
            obj = None
        return obj


class TradesListView(ConfiguredListView):
    model = Trade
    context_object_name = 'trades'
    template_name = 'petrolTrades.html'
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['petrol_list'] = Petrol.objects.all()
        context['cars'] = Car.objects.all()
        context['bonus_limit'] = settings.PETROL_BONUS_LIMIT
        return context


class TradeCreateView(CreateView):
    model = Trade
    success_url = reverse_lazy('trades_list')
    template_name = 'petrolTrades.html'
    form_class = TradeForm
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.member
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, error in form.errors.items():
            messages.error(self.request, error)

        return redirect(self.success_url)


class TradeDeleteView(DeleteView):
    model = Trade
    success_url = reverse_lazy('trades_list')
    http_method_names = ['post', ]
    oil_trades_page = reverse_lazy('oils_trades')
    petrol_cars_list_page = reverse_lazy('cars_list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Trade, pk=self.request.POST['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponse(success_url)


class ProductsListView(ConfiguredListView):
    model = Product
    context_object_name = 'products'
    template_name = 'productsList.html'
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(category__slug=self.kwargs['slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductsListView, self).get_context_data(**kwargs)
        context['product_category'] = ProductCategory.objects.get(slug=self.kwargs['slug'])
        return context


class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'price', 'remaining_quantity']
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products_list', kwargs=self.kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.category = ProductCategory.objects.get(slug=self.kwargs['slug'])
        form.instance.created_by = self.member
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ProductDeleteView(DeleteView):
    model = Product
    http_method_names = ['post', ]
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products_list', kwargs=self.kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Product, pk=self.request.POST['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponse(success_url)


class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'price', 'remaining_quantity']
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products_list', kwargs=self.kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Product, pk=self.request.POST['pk'])

    def form_valid(self, form):
        # form.instance.created_by = self.member
        return super().form_valid(form)


class ProductCheckInsListView(ConfiguredListView):
    model = ProductCheckIn
    context_object_name = 'productCheckIns'
    template_name = 'productCheckIns.html'
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return ProductCheckIn.objects.filter(product__category__slug=self.kwargs['slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(category__slug=self.kwargs['slug'])
        context['product_category'] = ProductCategory.objects.get(slug=self.kwargs['slug'])
        return context


class ProductCheckinCreateView(CreateView):
    model = ProductCheckIn
    # fields = ['checkin_product_quantity', 'date']
    template_name = 'productCheckIns.html'
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')
    form_class = ProductCheckInForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products_checkins', kwargs=self.kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.member
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ProductCheckinDeleteView(DeleteView):
    model = ProductCheckIn
    http_method_names = ['post', ]
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products_checkins', kwargs=self.kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(ProductCheckIn, pk=self.request.POST['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponse(success_url)


class ProductTradesListView(ConfiguredListView):
    model = ProductTrade
    context_object_name = 'productTrades'
    template_name = 'productTrades.html'
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.product_category = ProductCategory.objects.get(slug=self.kwargs['slug'])
        if not self.member.is_manager:  # if member is STAFF
            if self.member not in self.product_category.staffs.all():
                if self.member.is_general_staff:
                    return redirect(self.petrol_cars_list_page)
                if self.member.is_petrol_staff:
                    return redirect(self.petrol_cars_list_page)
                if self.member.is_oil_staff:
                    return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return ProductTrade.objects.filter(product__category__slug=self.kwargs['slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(category__slug=self.kwargs['slug'])
        context['product_category'] = ProductCategory.objects.get(slug=self.kwargs['slug'])
        return context


class ProductTradeCreateView(CreateView):
    model = ProductTrade
    # fields = ['product', 'tradePrice', 'sold_product_quantity', 'dateTime']
    # template_name = 'productTrades.html'
    form_class = ProductTradeForm
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.product_category = ProductCategory.objects.get(slug=self.kwargs['slug'])
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member not in self.product_category.staffs.all():
                if self.member.is_general_staff:
                    return redirect(self.petrol_cars_list_page)
                if self.member.is_petrol_staff:
                    return redirect(self.petrol_cars_list_page)
                if self.member.is_oil_staff:
                    return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products_trades', kwargs=self.kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.member
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, error in form.errors.items():
            messages.error(self.request, error)

        return redirect(self.get_success_url())
        # return super().form_invalid(form)


class ProductTradeDeleteView(DeleteView):
    model = ProductTrade
    http_method_names = ['post', ]
    petrol_cars_list_page = reverse_lazy('cars_list')
    oil_trades_page = reverse_lazy('oils_trades')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.member = Member.objects.get(username=self.request.user.username)
        if not self.member.is_manager:  # if member is STAFF
            if self.member.is_general_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_petrol_staff:
                return redirect(self.petrol_cars_list_page)
            if self.member.is_oil_staff:
                return redirect(self.oil_trades_page)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products_trades', kwargs=self.kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(ProductTrade, pk=self.request.POST['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponse(success_url)


def page_not_found_view(request, exception):
    response = render(request, '404.html')
    response.status_code = 404
    return response


def internal_server_error_view(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response
