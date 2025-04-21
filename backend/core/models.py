from django.db import models
from django.contrib.auth.models import User

class Consultoria(models.Model):
    nome = models.CharField(max_length=255)
    config = models.JSONField(default=dict)  # logo_url, primary_color, brand_name, subdomain, theme_class
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Consultoria'
        verbose_name_plural = 'Consultorias'

class ClienteFinal(models.Model):
    consultoria = models.ForeignKey(Consultoria, on_delete=models.CASCADE, related_name='clientes')
    nome = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.consultoria.nome}"

    class Meta:
        verbose_name = 'Cliente Final'
        verbose_name_plural = 'Clientes Finais'

class AmbienteCloud(models.Model):
    TIPOS_CLOUD = [
        ('AWS', 'AWS'),
        ('GCP', 'GCP'),
        ('Azure', 'Azure')
    ]

    cliente = models.ForeignKey(ClienteFinal, on_delete=models.CASCADE, related_name='ambientes')
    tipo = models.CharField(max_length=50, choices=TIPOS_CLOUD)
    credenciais = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cliente.nome}"

    class Meta:
        verbose_name = 'Ambiente Cloud'
        verbose_name_plural = 'Ambientes Cloud'

class Relatorio(models.Model):
    ambiente = models.ForeignKey(AmbienteCloud, on_delete=models.CASCADE, related_name='relatorios')
    titulo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50)
    resultado = models.JSONField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.ambiente}"

    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancelled', 'Cancelled')
    ]
    
    consultoria = models.ForeignKey(Consultoria, on_delete=models.CASCADE, related_name='subscriptions')
    stripe_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    plan = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.consultoria.nome} - {self.plan}"

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
