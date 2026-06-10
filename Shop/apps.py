from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Shop'

    #Inicializa o signals do app assim que o app iniciar também
    def ready(self):
        import Shop.signals 