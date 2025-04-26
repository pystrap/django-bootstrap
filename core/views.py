import os
import logging
from urllib.parse import urlparse

from django.views.generic import View
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
# Create your views here.


def index(request):
    parsed_endpoint = urlparse(settings.FRONTEND_APP_DIR)
    new_host = parsed_endpoint.netloc
    endpoint = request.build_absolute_uri().replace(request.get_host(), new_host)
    return render(request, 'redirect.html', {'endpoint': endpoint})


class FrontendAppView(View):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    def get(self, request):
        try:
            with open(os.path.join(settings.REACT_APP_DIR, 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            logging.exception('Production build of app not found')
            return HttpResponse(
                """
                This URL is only used when you have built the production
                version of the app.
                """,
                status=501,
            )