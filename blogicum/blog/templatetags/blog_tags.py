from django.template.defaultfilters import register


@register.filter(name='starts_with')
def starts_with(value: str, string: str):
    return value.strip().startswith(string)
