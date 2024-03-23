from django.utils import timezone


class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Your logic to update last_seen field
        if request.user.is_authenticated:
            if hasattr(request.user, 'last_seen'):
                request.user.last_seen = timezone.now()
                request.user.save()

        return response
