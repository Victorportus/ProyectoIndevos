import sys
import time
import board
import busio
import adafruit_sgp30
import adafruit_dht
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
import struct
import serial
import smtplib
import config
import os
import csv
import urllib.request
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Adafruit_IO import Client, Feed, RequestError

class Prototipo():
    def __init__(self):
        while True:
            Interruptor.prender(21)

            
            dic = Sensor().getData()
            Loader(dic)
            
            Interruptor.apagar(21)
            time.sleep(config.tiempoEntrePruebas * 60)

                
    def correo(mensaje):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(config.fromaddr, config.password)
            mensaje = mensaje
            server.sendmail(config.fromaddr, config.toaddr,mensaje)
            server.quit()
        except:
            pass
        
class Sensor():
    def __init__(self):
        try:
            self.connect()
            dic = self.getData()
        except:
            Interruptor.apagar(21)
            Interruptor.prender(20)
            Prototipo.correo("Verifica la conexion de los sensores")
                
    def connect(self):
        try:
            DHT22(board.D17, dic = self.getData())
            SDS011(dic = self.getData())            
            SGP30(bus = 6, dic = self.getData())
        except:
            Interruptor.apagar(21)
            Interruptor.prender(20)
            Prototipo.correo("Verifica la conexion de los sensores")
    
    def getData(self):
        try:
            return self.data
        except:
            self.data = {}
            return self.data
    def setData(self, p):
        self.data = p
        
class Loader():
    def __init__(self, d):
        Csv(d)
        try:
            Loader.pruebaInternet()
            GSheet(d)
            Adafruit(d)
            Thingspeak(d)            
        except (requests.ConnectionError, requests.Timeout):
            Interruptor.prender(20)
        
    def pruebaInternet():
        request = requests.get("http://www.google.com", timeout=5)
        Interruptor.prender(20)
        Interruptor.apagar(20)


class Csv():
    
    def __init__(self, d):
        self.header()
        self.prepCsv(d)
                
    def prepCsv(self, d):        
        data = (time.strftime("%m/%d/%y"), time.strftime("%H:%M"), d['temperatura'], d['humedad'], d['pmt'], d['eco'], d['tvoc'])
        f = open(config.archivoCSV, 'a')
        writer = csv.writer(f)
        writer.writerow(data)
        f.close()        
        
    def header(self):
        header = ["Date","Time","Temperature","Humidity","PMT2.5 µg/m3", "eCO2", "TVOC"]
        f = open(config.archivoCSV, 'a')
        writer = csv.writer(f)
        if os.stat(config.archivoCSV).st_size == 0:
            writer.writerow(header)
        f.close()


class Thingspeak():
    def __init__(self, d):
        self.loadTemp(d)
        time.sleep(15)
        self.loadHumi(d)
        time.sleep(15)
        self.loadPmt25(d)
        time.sleep(15)
        self.loadEco2(d)
        time.sleep(15)
        self.loadTvoc(d)
        
    def loadTemp(self, d):
        loadTemp = "https://api.thingspeak.com/update?api_key="+config.ThingspeakKey+"&field1="
        f = urllib.request.urlopen(loadTemp + str(d['temperatura']))
        f.read()
        f.close()
        
    def loadHumi(self, d):
        loadHumi = "https://api.thingspeak.com/update?api_key="+config.ThingspeakKey+"&field2="
        f = urllib.request.urlopen(loadHumi + str(d['humedad']))
        f.read()
        f.close()
        
    def loadPmt25(self, d):
        loadPmt25 = "https://api.thingspeak.com/update?api_key="+config.ThingspeakKey+"&field3="
        f = urllib.request.urlopen(loadPmt25 + str(d['pmt']))
        f.read()
        f.close()
        
    def loadEco2(self, d):
        loadEco2 = "https://api.thingspeak.com/update?api_key="+config.ThingspeakKey+"&field4="
        f = urllib.request.urlopen(loadEco2 + str(d['eco']))
        f.read()
        f.close()
        
    def loadTvoc(self, d):
        loadTvoc = "https://api.thingspeak.com/update?api_key="+config.ThingspeakKey+"&field5="
        f = urllib.request.urlopen(loadTvoc + str(d['tvoc']))
        f.read()
        f.close()
        
        
class GSheet():
    
    def __init__(self, d):        
        try:
            s = self.connectSheet()
            self.checkConnect(s)
            self.header(s)
            self.loadData(d, s)
        except:
            Prototipo.correo('No se puede conectar a Google API.')
        
    def connectSheet(self):
        gc = gspread.service_account(filename='mycredentials.json')
        gsheet = gc.open(config.nombreArchivoGoogleSheet)
        wsheet = gsheet.worksheet(config.nombreHojaGoogleSheet)
        return wsheet
    
    def checkConnect(self, s):
        cval = s.acell('A2').value
        
        
    def loadData(self, d, s):
        data = (time.strftime("%m/%d/%y"), time.strftime("%H:%M"), d['temperatura'], d['humedad'], d['pmt'], d['eco'], d['tvoc'])
        r = self.row(s)
        s.insert_row(data, r)
    
    def row(self, s):
        col_index = 1
        values_column = s.col_values(col_index)
        new_row_index = len(values_column) + 1
        return new_row_index
    
    def header(self, s):
        row_index = 1
        try:
            values_row = s.row_values(row_index)
        except:
            header = ("Date","Time","Temperature","Humidity","PMT2.5 µg/m3", "eCO2", "TVOC")
            s.insert_row(header, 1)


class Adafruit():
    def __init__(self, d):
        aio = self.connect()
        self.createLoadData(aio, d)
        
    def connect(self):        
        aio = Client(config.adafruitUsername, config.adafruitKey)
        return aio
    
    def createLoadData(self, aio, d):
        key = d.keys()
        for n  in key:
            self.createFeed(aio, n)
            self.loadData(d, aio, n)
            time.sleep(2)
    
    def createFeed(self, aio, n):
        try:
            f = aio.feeds(n)
        except:
            f = aio.create_feed(Feed(name=n))
    
    def loadData(self, d, aio, n):
        aio.send(n, d[n])
         
  
class SGP30(Sensor):    
    def __init__(self, bus, dic):
        try:
            sensor = self.connect(bus)
            self.read(sensor)
        except:
            Prototipo.correo("No se puede conectar con el sensor SGP30")
            self.setEco2("Fail")
            self.setTvoc("Fail")        
        self.dic(dic)
        
    def connect(self, bus):
        if bus == 1:
            i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        if bus == 6:
            i2c = busio.I2C(board.D1, board.D0, frequency=100000)
        sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
        sgp30.iaq_init()        
        sgp30.set_iaq_baseline(config.calibradoCO2, config.calibradoTvoc)
        return sgp30
    
    def read(self, s):
        eco2= 400
        tvoc= 0
        i = 0
        count = 0
        while eco2==400 and tvoc==0 and i < 3:
            time.sleep(1)
            eco2 = s.eCO2
            tvoc = s.TVOC
            self.setEco2(eco2)
            self.setTvoc(tvoc)
            count += 1
            if count > 10:
                count = 0
                s.set_iaq_baseline(38815, 39046)
                i += 1
        if i >= 3:
            self.setEco2("Fail")
            self.setTvoc("Fail")
                
    
    def getEco2(self):
        return self.eco2
    def setEco2(self, p):
        self.eco2 = p
        
    def getTvoc(self):
        return self.tvoc
    def setTvoc(self, p):
        self.tvoc = p

    def dic(self, dic):
        dic1 = {'eco' : self.getEco2(), 'tvoc' : self.getTvoc()}
        dic.update(dic1)
        Sensor.setData(self, dic)
        
        
class DHT22(Sensor):
    def __init__(self, pin, dic):
        sensor = self.connect(pin)
        self.read(sensor)
        self.dic(dic)
        
    def connect(self, pin):
        GPIO.setmode(GPIO.BCM)
        dhtDevice = adafruit_dht.DHT22(pin)
        return dhtDevice
    
    def read(self, dht):
        i = 0
        while i < 5:
            try:
                self.setTemp(dht.temperature)
                self.setHumi(dht.humidity)
                dht.exit()
                break
            except RuntimeError as error:
                i += 1
                time.sleep(2.0)
                continue
        if i >= 5:
            dht.exit()
            Prototipo.correo("No se puede leer sensor DHT22")
            self.setTemp("Fail")
            self.setHumi("Fail")
        
        
    def dic(self, dic):
        dic1 = {'temperatura' : self.getTemp(), 'humedad' : self.getHumi()}
        dic.update(dic1)
        Sensor.setData(self, dic)
        
    def setHumi(self, p):
        self.humi = p
    def getHumi(self):
        return self.humi
    
    def setTemp(self, p):
        self.temp = p
    def getTemp(self):
        return self.temp
    
    
class SDS011(Sensor):
    """Provides method to read from a SDS011 air particlate density sensor
    using UART.
    """

    HEAD = b'\xaa'
    TAIL = b'\xab'
    CMD_ID = b'\xb4'

    # The sent command is a read or a write
    READ = b"\x00"
    WRITE = b"\x01"

    REPORT_MODE_CMD = b"\x02"
    ACTIVE = b"\x00"
    PASSIVE = b"\x01"

    QUERY_CMD = b"\x04"

    # The sleep command ID
    SLEEP_CMD = b"\x06"
    # Sleep and work byte
    SLEEP = b"\x00"
    WORK = b"\x01"

    # The work period command ID
    WORK_PERIOD_CMD = b'\x08'

    def __init__(self, dic, serial_port = "/dev/ttyUSB0", baudrate=9600, timeout=2,
                 use_query_mode=True):
        """Initialise and open serial port.
        """
        self.ser = serial.Serial(port=serial_port,
                                 baudrate=baudrate,
                                 timeout=timeout)
        self.ser.flush()
        self.set_report_mode(active=not use_query_mode)
        self.sleep(sleep=False)
        time.sleep(10.0)
        self.query()
        self.sleep(sleep=True)
        self.dic(dic)

    def _execute(self, cmd_bytes):
        """Writes a byte sequence to the serial.
        """
        self.ser.write(cmd_bytes)

    def _get_reply(self):
        """Read reply from device."""
        raw = self.ser.read(size=10)
        data = raw[2:8]
        if len(data) == 0:
            return None
        if (sum(d for d in data) & 255) != raw[8]:
            return None  #TODO: also check cmd id
        return raw

    def cmd_begin(self):
        """Get command header and command ID bytes.
        @rtype: list
        """
        return self.HEAD + self.CMD_ID

    def set_report_mode(self, read=False, active=False):
        """Get sleep command. Does not contain checksum and tail.
        @rtype: list
        """
        cmd = self.cmd_begin()
        cmd += (self.REPORT_MODE_CMD
                + (self.READ if read else self.WRITE)
                + (self.ACTIVE if active else self.PASSIVE)
                + b"\x00" * 10)
        cmd = self._finish_cmd(cmd)
        self._execute(cmd)
        self._get_reply()

    def query(self):
        """Query the device and read the data.
        @return: Air particulate density in micrograms per cubic meter.
        @rtype: tuple(float, float) -> (PM2.5, PM10)
        """
        cmd = self.cmd_begin()
        cmd += (self.QUERY_CMD
                + b"\x00" * 12)
        cmd = self._finish_cmd(cmd)
        self._execute(cmd)

        raw = self._get_reply()
        if raw is None:
            return None  #TODO:
        data = struct.unpack('<HH', raw[2:6])
        pm25 = data[0] / 10.0
        pm10 = data[1] / 10.0
        self.setPmt25(pm25)
        return (pm25, pm10)
    
    def dic(self, dic):
        dic1 = {'pmt' : self.getPmt25()}
        dic.update(dic1)
        Sensor.setData(self, dic)
    
    def getPmt25(self):
        return self.pmt25
    def setPmt25(self, p):
        self.pmt25 = p

    def sleep(self, read=False, sleep=True):
        """Sleep/Wake up the sensor.
        @param sleep: Whether the device should sleep or work.
        @type sleep: bool
        """
        cmd = self.cmd_begin()
        cmd += (self.SLEEP_CMD
                + (self.READ if read else self.WRITE)
                + (self.SLEEP if sleep else self.WORK)
                + b"\x00" * 10)
        cmd = self._finish_cmd(cmd)
        self._execute(cmd)
        self._get_reply()

    def set_work_period(self, read=False, work_time=0):
        """Get work period command. Does not contain checksum and tail.
        @rtype: list
        """
        assert work_time >= 0 and work_time <= 30
        cmd = self.cmd_begin()
        cmd += (self.WORK_PERIOD_CMD
                + (self.READ if read else self.WRITE)
                + bytes([work_time])
                + b"\x00" * 10)
        cmd = self._finish_cmd(cmd)
        self._execute(cmd)
        self._get_reply()

    def _finish_cmd(self, cmd, id1=b"\xff", id2=b"\xff"):
        """Add device ID, checksum and tail bytes.
        @rtype: list
        """
        cmd += id1 + id2
        checksum = sum(d for d in cmd[2:]) % 256
        cmd += bytes([checksum]) + self.TAIL
        return cmd

    def _process_frame(self, data):
        """Process a SDS011 data frame.
        Byte positions:
            0 - Header
            1 - Command No.
            2,3 - PM2.5 low/high byte
            4,5 - PM10 low/high
            6,7 - ID bytes
            8 - Checksum - sum of bytes 2-7
            9 - Tail
        """
        raw = struct.unpack('<HHxxBBB', data[2:])
        checksum = sum(v for v in data[2:8]) % 256
        if checksum != data[8]:
            return None
        pm25 = raw[0] / 10.0
        pm10 = raw[1] / 10.0
        return (pm25, pm10)

    def read(self):
        """Read sensor data.
        @return: PM2.5 and PM10 concetration in micrograms per cude meter.
        @rtype: tuple(float, float) - first is PM2.5.
        """
        byte = 0
        while byte != self.HEAD:
            byte = self.ser.read(size=1)
            d = self.ser.read(size=10)
            if d[0:1] == b"\xc0":
                data = self._process_frame(byte + d)
                return data
            
class Interruptor(object):
    
    def __init__(self):
        self.prender()
        self.apagar()
        
    def prender(p):
        GPIO.setup(p, GPIO.OUT)
        GPIO.output(p, GPIO.HIGH)
        GPIO.output(p, GPIO.HIGH)
    
    def apagar(p):
        GPIO.output(p, GPIO.LOW)

Interruptor.prender(20)
Interruptor.apagar(20)   
    
    
if __name__ == "__main__":
    prototipo = Prototipo()
