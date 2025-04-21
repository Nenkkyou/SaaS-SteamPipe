from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import Consultoria
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            return None

        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        
        try:
            request.consultoria = Consultoria.objects.get(config__subdomain=subdomain)
            logger.info(f"Tenant identified: {request.consultoria.nome}")
        except Consultoria.DoesNotExist:
            request.consultoria = None
            logger.warning(f"No tenant found for subdomain: {subdomain}")
            if not request.path.startswith('/api/public/'):
                return HttpResponseForbidden("Invalid tenant")
