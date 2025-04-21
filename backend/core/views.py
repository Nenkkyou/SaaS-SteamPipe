from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Consultoria, ClienteFinal, AmbienteCloud, Relatorio, Subscription
from .serializers import (
    ConsultoriaSerializer, ClienteFinalSerializer, AmbienteCloudSerializer,
    RelatorioSerializer, SubscriptionSerializer, BrandingSerializer
)
from .utils import run_steampipe, setup_workspace, SteampipeError
import stripe
from django.conf import settings
import logging
import csv
from django.http import HttpResponse
from datetime import datetime

logger = logging.getLogger(__name__)

class BrandingView(APIView):
    permission_classes = []  # Public endpoint

    def get(self, request):
        if not request.consultoria:
            return Response({
                "error": "Tenant not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BrandingSerializer(request.consultoria)
        return Response(serializer.data)

class ConsultoriaViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Consultoria.objects.filter(id=self.request.consultoria.id)

class ClienteFinalViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteFinalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ClienteFinal.objects.filter(consultoria=self.request.consultoria)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        cliente = self.get_object()
        cliente.is_active = not cliente.is_active
        cliente.save()
        return Response({'status': 'success', 'is_active': cliente.is_active})

class AmbienteCloudViewSet(viewsets.ModelViewSet):
    serializer_class = AmbienteCloudSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AmbienteCloud.objects.filter(
            cliente__consultoria=self.request.consultoria
        )

    def perform_create(self, serializer):
        ambiente = serializer.save()
        try:
            setup_workspace(
                self.request.consultoria.id,
                ambiente.credenciais
            )
        except SteampipeError as e:
            logger.error(f"Failed to setup Steampipe workspace: {e}")
            ambiente.delete()
            raise

class RelatorioViewSet(viewsets.ModelViewSet):
    serializer_class = RelatorioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Relatorio.objects.filter(
            ambiente__cliente__consultoria=self.request.consultoria
        )

    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        relatorio = self.get_object()
        export_format = request.query_params.get('format', 'json')

        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="relatorio_{pk}_{datetime.now().strftime("%Y%m%d")}.csv"'
            
            writer = csv.writer(response)
            # Assuming resultado is a list of dictionaries
            if relatorio.resultado:
                # Write headers
                writer.writerow(relatorio.resultado[0].keys())
                # Write data rows
                for item in relatorio.resultado:
                    writer.writerow(item.values())
            return response

        # Default to JSON
        return Response(relatorio.resultado)

    @action(detail=False, methods=['post'])
    def run_query(self, request):
        ambiente_id = request.data.get('ambiente_id')
        query = request.data.get('query')
        titulo = request.data.get('titulo')
        tipo = request.data.get('tipo')

        ambiente = get_object_or_404(AmbienteCloud, id=ambiente_id)
        
        try:
            workspace_path = f"/tmp/steampipe/workspaces/{self.request.consultoria.id}"
            resultado = run_steampipe(query, workspace_path)
            
            relatorio = Relatorio.objects.create(
                ambiente=ambiente,
                titulo=titulo,
                tipo=tipo,
                resultado=resultado
            )
            
            serializer = self.get_serializer(relatorio)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except SteampipeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(consultoria=self.request.consultoria)

    @action(detail=False, methods=['post'])
    def create_checkout_session(self, request):
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': request.data.get('price_id'),
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.data.get('success_url', ''),
                cancel_url=request.data.get('cancel_url', ''),
                client_reference_id=str(self.request.consultoria.id)
            )
            return Response({'sessionId': checkout_session.id})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['POST'])
@permission_classes([])
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload=request.body,
            sig_header=request.META['HTTP_STRIPE_SIGNATURE'],
            secret=webhook_secret
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            consultoria_id = session['client_reference_id']
            
            # Create or update subscription
            Subscription.objects.update_or_create(
                consultoria_id=consultoria_id,
                defaults={
                    'stripe_id': session['subscription'],
                    'status': 'active',
                    'plan': session['display_items'][0]['plan']['id']
                }
            )
            
        return Response({'status': 'success'})
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
