from blog.handlers import BusinessLogicExceptionHandler, SC404ExceptionHandler, CSRFExceptionhandler, \
    SC500ExceptionHandler


class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.handlers = [
            BusinessLogicExceptionHandler(),
            SC404ExceptionHandler(),
            CSRFExceptionhandler(),
            # обязательно должен быть последним!!!
            SC500ExceptionHandler()
        ]

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        for h in self.handlers:
            if h.supports(exception):
                return h.handle(request, exception)
        return None
