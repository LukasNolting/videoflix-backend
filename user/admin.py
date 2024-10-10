from django.contrib import admin
from django.utils.html import format_html
from rest_framework.authtoken.models import Token
from videoflix_app.models import User

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'last_login', 'date_joined',
        'is_superuser', 'remember', 'get_auth_token'
    )
    list_filter = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        ('Personal Information', {'fields': ('username', 'email', 'first_name', 'last_name')}),
    )

    def get_auth_token(self, obj):
        """Zeigt das Auth-Token für den Benutzer an."""
        try:
            token = Token.objects.get(user=obj)
            return format_html(f'<strong>{token.key}</strong>')
        except Token.DoesNotExist:
            return 'Kein Token vorhanden'

    get_auth_token.short_description = 'Auth Token'  # Spaltenname im Admin-Bereich

# Registriere die benutzerdefinierte Admin-Klasse
admin.site.register(User, CustomUserAdmin)
