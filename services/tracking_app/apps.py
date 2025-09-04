from django.apps import AppConfig

class TrackingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services.tracking_app'
    verbose_name = 'User Interaction Tracking'

    def ready(self):
        # Asegura el registro de señales en runtime
        from . import signals  # noqa: F401
