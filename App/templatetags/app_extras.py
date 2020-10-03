from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def sold(oil, delta_months='12'):
    total = 0
    curTime = timezone.localtime(timezone.now())
    from_time = curTime - timezone.timedelta(days=int(delta_months)*30)
    for t in oil.trades.filter(dateTime__range=[from_time, curTime]).order_by('-dateTime'):
        total += t.litreSold
    return total


@register.filter
def last_checkin(oil):
    last_checkin = oil.checkins.order_by('-date').last()
    if last_checkin:
        return last_checkin.date.strftime("%b %d, %Y")
    else:
        return ''


@register.filter
def checkin_cost(checkin):
    cost = checkin.oil.price * checkin.bottles * checkin.oil.bottleVolume
    if cost:
        return round(cost, 2)
    else:
        return 0


@register.filter
def remaining_percent(sold, remainingLitres):
    try:
        if sold or sold > 0:
            return 100 - round(float(sold) / (float(remainingLitres) + float(sold)) * 100, 2)
        else:
            return 100
    except (ValueError, ZeroDivisionError):
        return None


@register.filter
def multiply(value, arg):
    try:
        if value:
            return float(value) * float(arg)
        else:
            return 0
    except ValueError:
        return None


@register.filter
def divide(value, arg):
    try:
        if value:
            return float(value) / float(arg)
        else:
            return None
    except (ValueError, ZeroDivisionError):
        return None


@register.filter
def get_item(dictionary, key):
    if dictionary:
        val = dictionary[key]
        if val:
            return val.data
    else:
        return ''


@register.filter
def get_dict_value_by_key(dictionary, key):
    if dictionary:
        return dictionary[key]
    else:
        return ''


@register.filter
def chart_height(oils):
    base_height = 300
    if oils:
        return base_height + (int(oils.__len__()) // 15) * 50
    else:
        return base_height
