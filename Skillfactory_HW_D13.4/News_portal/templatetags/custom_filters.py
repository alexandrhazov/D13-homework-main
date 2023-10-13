from django import template

register = template.Library()


@register.filter
def censor(value):
    # Список нежелательных слов, которые нужно заменить
    bad_words = ['шаг', 'делат', 'траст', 'цензурирования', 'лова', 'ценз', 'ильт', 'отл',]

    # Преобразование слов в символы "*"
    for word in bad_words:
        value = value.replace(word, '*' * len(word))

    return value


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    request = context['request']
    params = request.GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return params.urlencode()