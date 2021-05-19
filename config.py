fromaddr = "XXX@universidadean.edu.co"
password = "XXXXX"
toaddr = "XXX@universidadean.edu.co"

'''Seleccione el tiempo entre cada prueba en minutos, el timepo minimo entre cada prueba debe ser de 2 minutos'''
tiempoEntrePruebas = X

'''Calibracion SGP30'''
calibradoCO2 = XXXX
calibradoTvoc = XXXX

''' Datos guardados en CSV
Ingrese la ubicaion donde desea guardar el archivo con data .csv '''
archivoCSV = "/home/pi/Desktop/Tito/Proyecto/Indevos/data.csv"

''' Datos en la nube ThingSpeak
Cree una cuenta en thingspeak, cree un canal con los Temperatura, Humedad, PMT25, Eco2 y TVOC.
Deben ser creados en ese orden.
Ingrese el key del canal creado.'''
ThingspeakKey = "XXXX"

''' Datos en la nube google sheet
Luego de autorizar en la consola de cloud los servicios de google drive y google sheet,
genere credenciales de cuenta de servicio y guarde el archivo .json en la carpeta del prototipo.
Cree el archivo de google sheet y compartalo con 'client_email' del archivo json.
Ingrese el nombre del archivo creado y el nombre de la hoja donde se almacenara la data.'''
nombreArchivoGoogleSheet = "XXXX"
nombreHojaGoogleSheet = "XXXX"

''' Datos en la nube Adafruit Io'''
adafruitUsername = "XXXX"
adafruitKey = "XXXX"


