from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'exceptions/404.html', status=404)


def csrf_verification_failed(request, exception):
    return render(request, 'exceptions/403csrf.html', status=403)


def internal_server_error(request):
    return render(request, 'exceptions/500.html', status=500)
