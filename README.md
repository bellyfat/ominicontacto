Entorno de desarrollo

El entorno utilizado para desarrollo es Debian 8 Jessie

El sistema debe ser desarrollado usando Python 2.7 y virtualenv.

Para la instalación de algunos paquetes en virtualenv, puede ser necesario instalar paquetes en el sistema operativo.

Paquetes sugeridos:
sudo apt-get install virtualenv libcairo2-dev openssl nginx libpq-dev python-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev gcc libmysqlclient-dev python-virtualenv postgresql-9.4 postgresql-contrib postgresql-server-dev-9.4 python-mysqldb libjpeg-dev git vim postgresql-plpython-9.4

El sistema requiere que los siguientes sistemas estén funcionando:

    PostgreSql 9.4 o superior, con 'plpythonu'
        sudo apt-get install postgresql-plpython-9.4
        ANTES de crear la BD, ejecutar (con un usuario con permisos de administrador de Postgresql):
        $ createlang plpythonu template1

Armado inicial del entorno
--------------------------

    $ git clone git@bitbucket.org:freetechdesarrollo/ominicontacto.git
    $ cd ominicontacto/
    $ virtualenv -p python2.7 virtualenv
    $ . virtualenv/bin/activate
    $ pip install -r requirements.txt
    $ touch oml_settings_local.py



En el servidor 172.16.20.241

reiniciar el uwsgi: echo r > /tmp/.ominicontacto-uwsgi-fifo 

El proyecto se encuentra: /home/freetech/ominicontacto

Ejecucion del sistema desde uWSGI
---------------------------------

Existe un script que lanza la aplicación usando uWSGI.

Para utilizar el sistema con uWSGI:

freetech@fts-omni:~$ cd /home/freetech/ominicontacto

$ ./run_uwsgi.sh

### Armado inicial del entorno ###

Editar oml_settings_local.py para que contenga:


```
#!python
# -*- coding: utf-8 -*-

"""
Defaults para ambientes de desarrollo.

Para utilizar estos settings, crear ``oml_settings_local``
(en paquete ROOT de Python) con:

    from fts_web_settings_local_dev import *  # @UnusedWildImport
    SECRET_KEY = 'xxx' # Algun valor random

    if 'USE_PG' in os.environ:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'xxxxxxx',
                'USER': 'xxxxxxx',
                'PASSWORD': 'xxxxxxx',
                'CONN_MAX_AGE': 300,
                'ATOMIC_REQUESTS': True,
            }
        }

Y luego de eso, las customizaciones.

"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    "*",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's1+*bfrvb@=k@c&9=pm!0sijjewneu5p5rojil#q+!a2y&as-4'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'PORT': 5432,
        'NAME': 'kamailio',
        'USER': 'kamailio',
        'PASSWORD': 'kamailiorw',
        'CONN_MAX_AGE': 300,
        'ATOMIC_REQUESTS': True,
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, "static_root")
MEDIA_ROOT = os.path.join(BASE_DIR, '/home/FreeTech/media_root')

OML_OMNILEADS_IP = "172.16.20.241"

# Tiempo de session en segundo por ejemplo 10 minutos=600
SESSION_COOKIE_AGE = 600

# 'OML_QUEUE_FILENAME': donde se genera la config de queues. Asterisk debe estar configurado
# 'OML_ASTERISK_HOSTNAME': servidor donde se copiara la config de queues. Asterisk debe estar configurado
# 'OML_ASTERISK_REMOTEPATH': path del server donde se guardara. Asterisk debe estar configurado
# 'OML_SIP_FILENAME': donde se genera la config de los sip de los agentes. Asterisk debe estar configurado
# 'OML_QUEUES_FILENAME': donde se genera la config de queues. Asterisk debe estar configurado
#  para hacer un include de este archivo
# **** RECORDAR: revisar permisos y que existan los directorios ****
OML_QUEUE_FILENAME = "/home/freetech/extensions_fts_queues.conf"
OML_ASTERISK_HOSTNAME = "freetech@172.16.20.222"
OML_ASTERISK_REMOTEPATH = "/etc/asterisk/"
OML_SIP_FILENAME = "/etc/asterisk/sip_fts.conf"
OML_QUEUES_FILENAME = "/home/freetech/queues_fts.conf"
OML_BACKLIST_REMOTEPATH  = "/var/spool/asterisk/"

# parametros de conexion con base de datos mysql de asterisk
# modificar esto parametros con la conexion de base de datos correcta para que no tire error la ejecucion
DATABASE_MYSQL_ASTERISK = {
    'BASE': None,
    'HOST': None,
    'USER': None,
    'PASSWORD': None,
}

ASTERISK = {
    'USERNAME': None,  # Usuario para AMI
    'PASSWORD': None,  # Password para usuario para AMI
    'HTTP_AMI_URL': None,
    # URL usado por Daemon p/acceder a Asterisk AMI via HTTP
        # Ej:
        #    "http://1.2.3.4:7088"
}

# 'OML_RELOAD_CMD': comando a ejecutar para realizar el reload de la configuracion de Asterisk
# **** RECORDAR: revisar permisos, usuario, etc.
OML_RELOAD_CMD = '["ssh root@172.16.20.222",  "/usr/sbin/asterisk", "-rx", "dialplan reload"]'

# 'OML_GRABACIONES_URL': url donde se encuentra las grabaciones en elastix
# ejemplo "http://172.16.20.222/grabaciones"

OML_GRABACIONES_URL = "http://172.16.20.222/grabaciones"

# 'OML_SUPERVISION_URL': url donde se encuentra las grabaciones en elastix
# ejemplo "http://172.16.20.222:8090/Omnisup/index.php"

OML_SUPERVISION_URL = "http://172.16.20.222:8090/Omnisup/index.php"

# 'OML_KAMAILIO_IP': ip donde se encuentra kamailio
# ejemplo "172.16.20.219/255.255.255.255"
OML_KAMAILIO_IP = "172.16.20.219/255.255.255.255"

# 'OML_WOMBAT_URL': url donde se encuentra el discador de wombat
# ejemplo "http://172.16.20.222/wombat"

OML_WOMBAT_URL = "http://172.16.20.222/wombat"

# 'OML_WOMBAT_FILENAME': donde se alojara temporalmente los json de wombat
# ejemplo "/home/freetech/"

OML_WOMBAT_FILENAME = "/home/freetech/"

# 'OML_WOMBAT_USER': user para conectarse con la api de WOMBAT DIALER
# "user_test"

OML_WOMBAT_USER = "user_test"

# 'OML_WOMBAT_PASSWORD': password para ingresar con la api de WOMBAT DIALER
# "user123"

OML_WOMBAT_PASSWORD = "user123"

_logging_output_file = os.environ.get("OML_LOGFILE", "django.log")
assert os.path.split(_logging_output_file)[0] == "",\
    "La variable de entorno OML_LOGFILE solo debe contener " +\
    "el nombre del archivo, SIN directorios."
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)-15s [%(levelname)7s] '
                '%(name)20s - %(message)s')
        },
    },
    'filters': {
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/freetech/ominicontacto/{0}'.format(_logging_output_file),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    }
}

```

### Configuracion ssl para desarrollo ###
Generar certificado usando el siguiente el comando
```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
```