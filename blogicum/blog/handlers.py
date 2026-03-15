from abc import ABC, abstractmethod

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse, Http404, HttpRequest
from django.shortcuts import render

from blog.exceptions import BusinessError


class AbstractExceptionHandler(ABC):
    @abstractmethod
    def supports(self, exception: Exception) -> bool:
        pass

    @abstractmethod
    def handle(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        pass


class BusinessLogicExceptionHandler(AbstractExceptionHandler):
    def supports(self, exception: Exception) -> bool:
        return isinstance(exception, BusinessError)

    def handle(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        context = {
            'error_code': exception.code if hasattr(exception, 'code') else 'business_error',
            'error_message': str(exception),
        }
        return render(request, 'pages/business_error.html', context=context, status=400)


class SC404ExceptionHandler(AbstractExceptionHandler):
    def supports(self, exception: Exception) -> bool:
        return isinstance(exception, Http404)

    def handle(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        return render(request, 'pages/404.html', status=404)


class CSRFExceptionhandler(AbstractExceptionHandler):
    def supports(self, exception: Exception) -> bool:
        return isinstance(exception, SuspiciousOperation)

    def handle(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        return render(request, 'pages/403csrf.html', status=403)


class SC500ExceptionHandler(AbstractExceptionHandler):
    def supports(self, exception: Exception) -> bool:
        return True

    def handle(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        return render(request, 'pages/500.html', status=500)
