# coding: utf-8
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import datetime
from nagios import *
from fecha import *
from twill.commands import *
import locale

import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Encoders import encode_base64
from email import Encoders

from config import CORREOS, EQUIPO, ACTIVIDADES, TEXTOS, NOTAS, ALERTAS, PIE_PAGINA, HOST_CACTI, LOGO, USER_WEB_CACTI, PASSWD_WEB_CACTI, SENDER_MAIL, MAIL_SERVER, PORT
#from settings import USER_WEB_CACTI, PASSWD_WEB_CACTI

from mem import *

class libreria:
    locale.setlocale(locale.LC_ALL,('es_MX','UTF8'))
    path = os.path.abspath(os.path.dirname(__file__)) + "/"
    nagios = nagios()
    centroPagina = ((inch * 8.5) / 2) - inch
    alturaNoPagina = -40
    altoImagen = 1.5 * inch
    anchoImagen = 3.6 * inch
    fileName = ""
    logo = path + LOGO
    posY = 9

    #lista de imagenes
    listaImagenes = []
    FECHA = ''
    def leeFECHA(self):
        #FECHA de memcache
        self.FECHA = MC.get("FECHA")
    
    def nuevoDocumento(self, fileName, title):
        self.fileName = fileName
        print self.fileName
        c = canvas.Canvas(fileName, pagesize=letter)
        c.translate(inch,inch)
        c.setTitle(title)
        self.posY = 9
        
        return c
        
    def nuevaPagina(self,c):
        c.showPage()
        c.translate(inch,inch)
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.345, 0.345, 0.345)
        c.drawCentredString(self.centroPagina, self.alturaNoPagina, str(c.getPageNumber()))
        self.posY = 9
        c.drawImage(self.logo, -0.3 * inch, inch * 9.1, 120, 30)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 12)
        
    def insertarTitulo(self, titulo, posY, c):
        c.setFillColorRGB(0, 0.070, 0.431)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0, inch * posY, titulo)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 12)
        posY -= 0.4
        self.posY = posY
        
    def verificaEspacioPagina(self, posY, espacioNecesario):
        if posY >= espacioNecesario:
            return True
        else:
            return False
        
    def insertarEncabezado(self, c, servidor, fechaInicio, fechaFin):
        fecha1 = fechaInicio.timetuple()
        fecha2 = fechaFin.timetuple()
        fecha = "Del " + str(fecha1.tm_mday) + " al " + str(fecha2.tm_mday) + " de " + fechaInicio.strftime("%B") + " de " + str(fecha1.tm_year)
        
        posY = self.posY
        c.setFont("Helvetica", 10)
        c.drawImage(self.logo, -0.3 * inch, inch * 9.1, 120, 30)
        
        c.setFillColorRGB(0.345,0.345,0.345)
        c.drawRightString(inch * 6.5, inch * posY, "Reporte Mensual")
        
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(0, 0.070, 0.431)
        posY -= 0.25
        c.drawRightString(inch * 6.5, inch * posY, servidor)
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.49, 0.137, 0)
        posY -= 0.20
        c.drawRightString(inch * 6.5, inch * posY, fecha)
        
        c.setFont("Helvetica", 12)
        c.setFillColorRGB(0, 0, 0)
        posY -= 0.7
        c.drawString(0, inch * posY, TEXTOS[0].strip())
        posY -= 0.5
        for i in EQUIPO:
            c.drawString(0, inch * posY, i[0].strip())
            c.drawString(inch * 2, inch * posY, i[1].strip())
            c.drawString(inch * 5, inch * posY, i[2].strip())
            posY -= 0.2
            
        posY -= 0.3
        self.insertarTitulo("Actividades diarias", posY, c)
        posY = self.posY
        c.drawString(0, inch * posY, TEXTOS[1].strip())
        posY -= 0.4 
        for i in ACTIVIDADES:
            c.drawString(0, inch * posY, "        -    " + i.strip())
            posY -= 0.2
        
        posY -= 0.3
        self.insertarTitulo("Monitoreo de rendimiento", posY, c)
        posY = self.posY
        
        c.drawString(0, inch * posY, TEXTOS[2].strip())
        posY -= 0.3
        c.drawString(0, inch * posY, TEXTOS[3].strip())
        
        self.posY = posY
        
        #Pie de pagina
        auxPosY = -0.35 * inch
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.345,0.345,0.345)
        for i in PIE_PAGINA:
            c.drawString(0, auxPosY, i)
            auxPosY -= 0.12 * inch
        c.setFont("Helvetica", 12)
        c.setFillColorRGB(0, 0, 0)
        
    def insertaImagenes(self, c, listaImagenes, servidor):
        posY = self.posY
        posY -= 0.4
        for i in listaImagenes:
            if not self.verificaEspacioPagina(posY, (self.altoImagen / inch)):
                self.nuevaPagina(c)
                posY = self.posY
            
            if i.find(servidor) > 1:
                posY -= self.altoImagen / inch
                c.drawImage(self.path + i, (self.centroPagina - (self.anchoImagen /2)), posY * inch, self.anchoImagen, self.altoImagen)
                posY -= 0.2

        posY -= 0.1
        self.insertarNota(c, 0, posY, 0.4)
        posY = self.posY
        
        posY -= 0.1
        self.insertarTitulo("Actualizaciones", posY, c)
        posY = self.posY
        
        posY += 0.2
        self.insertarNota(c, 1, posY, 0.6)
        posY = self.posY
        
        self.nuevaPagina(c)
    
    def insertarNota(self, c, noNota, posY, alto):
        if not (self.verificaEspacioPagina(posY, alto)):
            self.nuevaPagina(c)
            posY = self.posY

        posY -= alto
        c.setFillColorRGB(1,1,0.3)
        c.setStrokeColorRGB(1, 1, 1)
        c.rect(0 ,posY * inch , inch * 6.5, inch * alto, fill=1)

        c.setStrokeColorRGB(0.49, 0.137, 0)
        c.line(0, posY * inch, inch * 6.5, posY * inch)
        c.line(0, (posY + alto) * inch, inch * 6.5, (posY + alto) * inch)
        
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(0.49, 0.137, 0)
        c.drawString(0, (posY + (alto - 0.16)) * inch, "  Nota:")
        c.drawString(0, (posY + (alto - 0.32)) * inch, "  " + NOTAS[noNota].strip())
        if(noNota == 1):
            c.drawString(0, (posY + (alto - 0.48)) * inch, "  " + NOTAS[noNota + 1].strip())
        
        c.setFont("Helvetica", 12)
        c.setFillColorRGB(0,0,0)
        posY -= 0.4
        self.posY = posY

    def insertarLogs(self, c, logs, servidor):
        posY = self.posY
        #print posY
        posY -= 0.2
        self.insertarTitulo("Registro de Alertas", posY, c)
        posY = self.posY
        
        posY += 0.2
        self.insertarNota(c, 3, posY, 0.4)
        posY = self.posY
        
        ExisteLog = False
        for i in logs:
            if not self.verificaEspacioPagina(posY, 0.18):
                self.nuevaPagina(c)
                posY = self.posY
                posY -= 0.2
                
            c.setFont("Helvetica", 8)
            if i.find(servidor) > 1:
                ExisteLog = True
                a = i
                a = a[:129]
                a = a.split(' ')
                b = ''
                for j in a:
                    b += j + " "
                b = b.strip()
                c.drawString(0, posY * inch, b.replace(servidor + ";", ""))
                posY -= 0.17
            
        if not ExisteLog:
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(0,0,0)
            c.drawString(0, posY * inch, TEXTOS[4])
        
    def obtenerLogNagios(self, listaServidores):
        nagios = self.nagios
        nagios.inicio()
        nagios.setListaServidores(listaServidores)
        nagios.guardaHistorial(ALERTAS)
        nagios.cambiaFecha()
        return nagios.getListaLog()
    
    def getListaImagenes(self):
        return self.listaImagenes
        
    def generarImagenes(self, listaCacti):
        user = USER_WEB_CACTI
        pw = PASSWD_WEB_CACTI
        
        Fecha = fecha()
        hoy = Fecha.getNow(self.FECHA)
        final = Fecha.getUltimoDia(hoy)
        primero = Fecha.getPrimerDia(final)
        #cambiamos a formato timestamp
        final = time.mktime(final.timetuple())
        primero = time.mktime(primero.timetuple())
        #combertimos a string el timestamp
        final = str(int(final))
        primero = str(int(primero))
        
        #go('http://10.164.90.15/cacti/')
        go(HOST_CACTI)
        fv("1", "login_username", user)
        fv("1", "login_password", pw)
        submit("None")
        
        #imagenesLista
        listaImagenes = self.listaImagenes
        
        for i in listaCacti:
            #iniciamos la variable url para indicar los identificadores
            url = HOST_CACTI + "/graph.php?action=properties&local_graph_id=<ID>&rra_id=0&graph_start=<START>&graph_end=<END>"
            #sustituimos identificadores
            url = url.replace("<ID>", str(i[2]))
            url = url.replace("<START>", primero)
            url = url.replace("<END>", final)
            #abrimos url
            go(url)

            a = show()
            a = a.split("<PRE>")[1].split("</PRE>")[0]
            a = a.replace("&quot;", "\"")

            fileName = a.split("--title=")[1].split("'")[1]
            if fileName[-1] == '/':
                fileName = fileName[:-4]
            fileName = fileName.replace(" - ", "-")
            fileName = fileName.replace(" ", "-")
            fileName = fileName.replace(",", "")
            fileName = fileName.replace("(", "[")
            fileName = fileName.replace(")", "]")
	    fileName = fileName.replace("/","-")
            cmd = a + " > " + self.path + "imagenes/" + fileName + ".png"
            #agregamos la ruta de la imagen a la lista
            listaImagenes.append("imagenes/" + fileName + ".png")
            os.system(cmd)
    
    def enviaCorreo(self, listaServidores, EMAIL_TO):
        #igualamos variable del import para poderla modificar
        CORREOSa = CORREOS
        #comparamos si existe un correo para cambiar el correo de envio por default
        if len(EMAIL_TO) > 3:
            CORREOSa = [EMAIL_TO]
        #revisamos si es ejecutado en la fecha actual
        if len(str(self.FECHA)) < 5:
            f = fecha().getNow(self.FECHA)
        else:
            f = fecha().getNow(self.FECHA) - datetime.timedelta(days=32)
        #mostramos ano y mes en que se esta generando el reporte
        f = str(f.year) + '-' + str(f.month).zfill(2)
        # Creamos objeto Multipart, quien ser� el recipiente que enviaremos
        msg = MIMEMultipart()
        msg['From']=SENDER_MAIL
        msg['Subject']="Reporte Mensual de monitoreo [" + f + "]"
        msg['X-Mailer'] = "Python X-Mailer"
        
        texto = """
        Reporte Mensual de los servidores monitoreados por Interalia
        """
        
        msg.attach(MIMEText(texto, 'plain', 'UTF-8'))
        
        #adjuntamos PDF
        for i in listaServidores:
            file = ("pdf/" + i + "[" + f + "]" + ".pdf").lower()
            part = MIMEBase('application', "pdf")
            part.set_payload(open(self.path + file, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
            msg.attach(part)
            
        #conectamos
        mailServer = smtplib.SMTP(MAIL_SERVER,PORT)
        # Enviamos
        for correo in CORREOSa:
            msg['To'] = correo.strip()
            mailServer.sendmail(SENDER_MAIL, correo.strip(), msg.as_string())
            print "CORREO a: ", correo.strip(), " enviado."
        # Cerramos conexi�n
        mailServer.close()
