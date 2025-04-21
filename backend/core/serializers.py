from rest_framework import serializers
from .models import Consultoria, ClienteFinal, AmbienteCloud, Relatorio, Subscription

class ConsultoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultoria
        fields = ['id', 'nome', 'config', 'created_at', 'updated_at']

class ClienteFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteFinal
        fields = ['id', 'consultoria', 'nome', 'is_active', 'created_at', 'updated_at']

class AmbienteCloudSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmbienteCloud
        fields = ['id', 'cliente', 'tipo', 'credenciais', 'created_at', 'updated_at']
        extra_kwargs = {
            'credenciais': {'write_only': True}  # Ensure credentials are never sent in responses
        }

class RelatorioSerializer(serializers.ModelSerializer):
    ambiente_details = AmbienteCloudSerializer(source='ambiente', read_only=True)

    class Meta:
        model = Relatorio
        fields = ['id', 'ambiente', 'ambiente_details', 'titulo', 'tipo', 'resultado', 'criado_em']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'consultoria', 'stripe_id', 'status', 'plan', 'created_at', 'updated_at']
        extra_kwargs = {
            'stripe_id': {'write_only': True}  # Ensure Stripe ID is never sent in responses
        }

class BrandingSerializer(serializers.ModelSerializer):
    """Serializer for returning branding information"""
    class Meta:
        model = Consultoria
        fields = ['nome', 'config']
