import datetime as d


def year(request):
    """Добавляет переменную с текущим годом"""
    return {
        'year': d.datetime.today().year,
    }
