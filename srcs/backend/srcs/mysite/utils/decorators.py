from django.http import JsonResponse

def require_http_methods(methods):
    def decorator(f):
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse({"error": "Method not allowed"}, status=405)
            return f(request, args, kwargs)
        return wrapper
    return decorator
