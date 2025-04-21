from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConsultoriaViewSet,
    ClienteFinalViewSet,
    AmbienteCloudViewSet,
    RelatorioViewSet,
    SubscriptionViewSet,
    BrandingView,
    stripe_webhook
)

router = DefaultRouter()
router.register(r'consultorias', ConsultoriaViewSet, basename='consultoria')
router.register(r'clientes', ClienteFinalViewSet, basename='cliente')
router.register(r'ambientes', AmbienteCloudViewSet, basename='ambiente')
router.register(r'relatorios', RelatorioViewSet, basename='relatorio')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
    path('branding/', BrandingView.as_view(), name='branding'),
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
