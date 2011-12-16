# coding: utf-8
import re
#Archvio de configuraciones para Reportes

#lista de correos para enviar los reportes
CORREOS = [
	'',
	]

#Sender mail
SENDER_MAIL = ''

#Servidor correo
MAIL_SERVER = ''
PORT = 25

#lista de equipos de incidencias
#Nombre, mail, telefono
EQUIPO = [
	['', '', ''],
	]

#lista de actividades
ACTIVIDADES = [
	'',
	]

#Textos
TEXTOS = [
	'',
	]

#Notas
NOTAS = [
	'',
	]

#Mostrar alertas de nagios
ALERTAS = [
	'',
	]

PIE_PAGINA = [
	'',
	]

HOST_CACTI = ''

LOGO = ''

EMAIL_TO = ''
HOST_SERVER = ''
FECHA = ''

#Datos CACTI base de datos
USER_CACTI = ''
DATA_BASE_CACTI = ''
PASSWD_CACTI = ''

#Datos CACTI graficas
USER_WEB_CACTI = ''
PASSWD_WEB_CACTI = ''

#Ruta logs nagios
NAGIOS_LOG = ''

email_re = re.compile(
	r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
	r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
	r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

try:
	from local_settings import *
except ImportError:
	pass
