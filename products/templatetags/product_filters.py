from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    try:
        return float(str(value).replace(',', '')) - float(str(arg).replace(',', ''))
    except (ValueError, TypeError):
        return 0