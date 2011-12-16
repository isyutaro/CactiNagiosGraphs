import MySQLdb
#from settings import USER_CACTI, DATA_BASE_CACTI, PASSWD_CACTI
from config import USER_CACTI, DATA_BASE_CACTI, PASSWD_CACTI

class SQL:
	def getListaCacti(self, HOST_SERVER):
		db = MySQLdb.connect(user=USER_CACTI, db=DATA_BASE_CACTI, passwd=PASSWD_CACTI, host='localhost')
		cursor = db.cursor()
		cursor.execute('select graph_templates.name, host.description, graph_local.id from host, graph_local, graph_templates where host.id=graph_local.host_id and graph_templates.id=graph_local.graph_template_id and host.disabled!="on" and host.description like "' + HOST_SERVER + '%"')
		lista = cursor.fetchall()
		db.close()
		return lista

