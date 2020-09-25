from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .models import OilTrade, OilCheckIn, Oil, Car, Trade, CarModel, Petrol
from .forms import OilTradeForm, TradeForm


class IndexView(TemplateView):
    template_name = 'index.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        currentTime = timezone.localtime(timezone.now())
        last_year_range = [(currentTime - timezone.timedelta(days=356)), currentTime]

        context = super(IndexView, self).get_context_data(**kwargs)

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

        context['totalSold'] = 0

        for o in Oil.objects.all():
            context['oilTrades'][o.name] = []
            context['oilTrades'][o.name] += o.trades.filter(dateTime__range=last_year_range).order_by('dateTime').values('oil', 'litreSold', 'tradePrice', 'dateTime')

            context['oils'][o.name] = o

            context['totalRemaining'] += o.RemainingLitres

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

        return context


class OilsListView(ListView):
    model = Oil
    context_object_name = 'oils'
    template_name = 'oilsList.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class OilCreateView(CreateView):
    model = Oil
    fields = ['name', 'price', 'RemainingLitres', 'RemainingBottles', 'bottleVolume', 'color']
    success_url = reverse_lazy('oils_list')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # form.instance.created_by = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OilDeleteView(DeleteView):
    model = Oil
    success_url = reverse_lazy('oils_list')

    http_method_names = ['post', ]

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

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Oil, name=self.request.POST['oldName'])

    def form_valid(self, form):
        form.instance.name = self.request.POST['oldName']
        return super().form_valid(form)


class OilCheckInsListView(ListView):
    model = OilCheckIn
    context_object_name = 'oilCheckIns'
    template_name = 'oilCheckIns.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the oils
        context['oils'] = Oil.objects.all()
        return context


class OilCheckinCreateView(CreateView):
    model = OilCheckIn
    fields = ['oil', 'bottles', 'date']
    success_url = reverse_lazy('oils_checkins')
    template_name = 'oilCheckIns.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # form.instance.created_by = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OilCheckinDeleteView(DeleteView):
    model = OilCheckIn
    success_url = reverse_lazy('oils_checkins')

    http_method_names = ['post', ]

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


class OilTradesListView(ListView):
    model = OilTrade
    context_object_name = 'oilTrades'
    template_name = 'oilsTrades.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the oils
        context['oils'] = Oil.objects.all()
        return context


class OilTradeCreateView(CreateView):
    model = OilTrade
    # fields = ['oil', 'litreSold', 'dateTime']
    success_url = reverse_lazy('oils_trades')
    template_name = 'oilsTrades.html'
    form_class = OilTradeForm

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        trade = form.instance
        if trade.oil.RemainingLitres < trade.litreSold:
            return redirect(self.success_url, form=form)

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OilTradeDeleteView(DeleteView):
    model = OilTrade
    success_url = reverse_lazy('oils_trades')

    http_method_names = ['post', ]

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


class CarsListView(ListView):
    model = Car
    context_object_name = 'cars'
    template_name = 'carsList.html'

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the oils
        context['carModels'] = CarModel.objects.all()
        return context


class CarCreateView(CreateView):
    model = Car
    fields = ['carNumber', 'model']
    success_url = reverse_lazy('cars_list')
    template_name = 'carsList.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # form.instance.created_by = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class CarDeleteView(DeleteView):
    model = Car
    success_url = reverse_lazy('cars_list')

    http_method_names = ['post', ]

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

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Car, carNumber=self.request.POST['carNumber'])

    def form_valid(self, form):
        trades = form.instance.get_trades()
        if trades['litre'] >= 500:
            form.instance.used_bonuses += 1
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class TradesListView(ListView):
    model = Trade
    context_object_name = 'trades'
    template_name = 'petrolTrades.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the oils
        context['petrol_list'] = Petrol.objects.all()
        context['cars'] = Car.objects.all()
        return context


class TradeCreateView(CreateView):
    model = Trade
    success_url = reverse_lazy('trades_list')
    template_name = 'petrolTrades.html'
    form_class = TradeForm

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class TradeDeleteView(DeleteView):
    model = Trade
    success_url = reverse_lazy('trades_list')

    http_method_names = ['post', ]

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


def page_not_found_view(request, exception):
    response = render(request, '404.html')
    response.status_code = 404
    return response


def internal_server_error_view(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response
