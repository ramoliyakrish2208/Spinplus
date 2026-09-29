from django.apps import AppConfig
from django.db.backends.signals import connection_created

def configure_sqlite_connection(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA journal_mode = WAL;')
            cursor.execute('PRAGMA synchronous = NORMAL;')
            cursor.execute('PRAGMA busy_timeout = 20000;')
            cursor.execute('PRAGMA cache_size = -64000;')
            cursor.execute('PRAGMA temp_store = MEMORY;')
            cursor.execute('PRAGMA foreign_keys = ON;')


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        connection_created.connect(configure_sqlite_connection)
