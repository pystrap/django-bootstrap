from django.http import HttpResponse
from rest_framework.generics import get_object_or_404
from .models import EmailTemplate
from rest_framework.decorators import api_view


@api_view(['GET'])
def index(request):
    name = request.query_params.get('template', None)
    template = get_object_or_404(EmailTemplate, name=name)
    if template.msg_html:
        return HttpResponse(template.msg_html)
    else:
        return HttpResponse('Could not load template')
