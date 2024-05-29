from django.apps import AppConfig

class DokterManagementAppConfig(AppConfig):
    name = 'dokter_management_app'

    # def ready(self):
    #     # This line ensures that the signals are imported and thus registered
    #     import dokter_management_app.signals
