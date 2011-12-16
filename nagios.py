import os, datetime, time
import re
from fecha import *
from mem import *
#from settings import NAGIOS_LOG
from config import NAGIOS_LOG

class nagios:
        #FECHA de memcache
        FECHA = ''
        fecha = ''
        hoy = ''
        dia = ''
        lista = ''
        listaServidores = []
        listaNagios = []
        logNagios = ''
        diaAux = ''
        def leeFECHA(self):
            self.FECHA = MC.get("FECHA")
        def inicio(self):
            #Obtenemos la fecha para los logs
            self.fecha=fecha()
            self.leeFECHA()
            hoy=self.fecha.getNow(self.FECHA)
            dia=self.fecha.getUltimoDia(hoy)
            #variable auxiliar para tener acceso al log siguiente del mes actual
            self.diaAux = dia
            dia=dia.strftime("%m-*-%Y")
            #Ruta de los logs
            ruta = NAGIOS_LOG
            cmd="ls " + ruta + "*-" + dia + "* " + ruta + "*-" + str(self.diaAux.month+1) + "-01-" + str(self.diaAux.year) + "*"
            aux=os.popen(cmd)
            #lista de logs del mes anterior
            self.lista=aux.read().split()
            self.listaServidores = []
            self.listaLogNagios = []
            self.logNagios = ""
            
        def setListaServidores(self, listaServidores):
            nagios.listaServidores = listaServidores
            
        def getLista(self):
                return nagios.lista
        
        def getListaLog(self):
                return nagios.listaLogNagios

        def getListaServidores(self):
                return nagios.listaServidores
            
        def guardaHistorial(self, alertas):
            #alert = '| egrep -w \"'
            #for i in alertas:
            #    alert += i.strip() + "|"
            
            #alert = alert[:-1] + "\""
	    alert = '| grep '
	    for i in alertas:
		alert += i.strip() + " | grep "
	    alert = alert[:-8]
            for i in range(len(nagios.listaServidores)):
                for j in range(len(self.lista)):
                    cmd='grep ' + nagios.listaServidores[i] + " " + self.lista[j] + " | grep \"SERVICE ALERT\" " + alert
                    aux=os.popen(cmd)
                    nagios.logNagios += aux.read()
                 
            nagios.listaLogNagios = nagios.logNagios.split('\n')
            del(nagios.listaLogNagios[-1])
                
        def cambiaFecha(self):
                formato="[%b-%d %H:%M]"
                #patron para obtener la fecha que esta en stamp del log
                pattern=re.compile('\ .*', re.I | re.S)
                aux = []
                
                for i in nagios.listaLogNagios:
                    fechaBien = (datetime.datetime.fromtimestamp(float(i.split("[")[1].split("]")[0])).strftime(formato))
                    aux2 = self.diaAux.strftime(formato).split('[')[1].split('-')[0]
                    #checamos que se encuentre en el log el mes del reporte
                    if(fechaBien.find(aux2) > 0):
                        remplazo=pattern.sub("", i)
                        i = i.replace(remplazo, fechaBien)
                        i = i.replace("SERVICE ALERT:","")
                        aux.append(i)

                nagios.listaLogNagios = aux
