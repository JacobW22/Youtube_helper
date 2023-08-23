from django.utils import timezone
import zoneinfo

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # get django_timezone from cookie
            tzname = request.COOKIES.get("django_timezone")
            timezone.activate(zoneinfo.ZoneInfo(tzname))

        except Exception:
            timezone.deactivate()

        return self.get_response(request)