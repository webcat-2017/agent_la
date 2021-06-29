import logging
import win32event
import win32serviceutil
import win32service
import servicemanager
import sys
import configparser
import time
import winreg as reg
import socket
import sensors
import pickle
import struct
from _thread import *
import threading
import ssl


class Agent(win32serviceutil.ServiceFramework):
    _svc_name_ = 'AgentLA'
    _svc_display_name_ = 'AgentLA'
    _svc_description_ = 'Lazy admin agent 1.0'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isAlive = True
        self.lock = threading.Lock()
        self.status_conn = False
        self.last_record = 0
        self.threads = {'uptime': False, }
        self.thread_is_alive = True

        with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\AgentLA") as h:
            self.path = reg.EnumValue(h, 3)[1].strip("la_service.exe")
            #self.path = r"D:\myApp\AgentLA\\"

        self.config = configparser.ConfigParser()
        self.config.read(self.path + 'config.ini', encoding='utf-8')

        # ssl and socket
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.path + r"ssl\server.crt")
        context.load_cert_chain(certfile=self.path + r"\ssl\client.crt", keyfile=self.path + r"\ssl\client.key")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        self.client_conn = context.wrap_socket(sock, server_side=False, server_hostname="LAServer")

        logging.basicConfig(
            level=logging.INFO,
            filename=self.path + "AgentLA.log",
            format='[AgentLA] %(asctime)s %(levelname)s %(message)s')

    def uptime(self, lock, is_alive):
        while is_alive:
            print("uptime while", time.ctime(), get_ident(), sep="---")
            data_to_server = dict()
            data_to_server.update({'name_id': self.config['client']['name_id']})
            data_to_server.update(sensors.Sensor.get_uptime())
            try:
                serialized_data = pickle.dumps(data_to_server)
                with lock:
                    self.client_conn.sendall(struct.pack('>I', len(serialized_data)))
                    self.client_conn.sendall(serialized_data)

                    data_size = struct.unpack('>I', self.client_conn.recv(4))[0]
                    received_payload = b""
                    reamining_payload_size = data_size
                    while reamining_payload_size != 0:
                        received_payload += self.client_conn.recv(reamining_payload_size)
                        reamining_payload_size = data_size - len(received_payload)
                    pickle.loads(received_payload)
            except:
                self.status_conn = True
                self.client_conn.close()
                is_alive = False
                self.threads.update({'uptime': False})

            time.sleep(1)

    def hwm(self, lock):
        while self.isAlive:
            data_to_server = dict()
            data_to_server.update({'name_id': self.config['client']['name_id']})
            data_to_server.update(sensors.Sensor.get_hwm())
            try:
                serialized_data = pickle.dumps(data_to_server)
                lock.acquire()
                self.client_conn.sendall(struct.pack('>I', len(serialized_data)))
                self.client_conn.sendall(serialized_data)
                lock.release()
            except:
                pass
            time.sleep(2)

    def disk_space(self, lock):
        while self.isAlive:
            data_to_server = dict()
            data_to_server.update({'name_id': self.config['client']['name_id']})
            data_to_server.update(sensors.Sensor.get_disk_space())
            try:
                serialized_data = pickle.dumps(data_to_server)
                lock.acquire()
                self.client_conn.sendall(struct.pack('>I', len(serialized_data)))
                self.client_conn.sendall(serialized_data)
                lock.release()
            except:
                pass
            time.sleep(5)

    def services(self, lock):
        while self.isAlive:
            data_to_server = dict()
            data_to_server.update({'name_id': self.config['client']['name_id']})
            data_to_server.update(sensors.Sensor.get_services())
            try:
                serialized_data = pickle.dumps(data_to_server)
                lock.acquire()
                self.client_conn.sendall(struct.pack('>I', len(serialized_data)))
                self.client_conn.sendall(serialized_data)
                lock.release()
            except:
                pass
            time.sleep(10)

    def smart(self, lock):
        while self.isAlive:
            data_to_server = dict()
            data_to_server.update({'name_id': self.config['client']['name_id']})
            data_to_server.update(sensors.Sensor.get_smart())
            try:
                serialized_data = pickle.dumps(data_to_server)
                lock.acquire()
                self.client_conn.sendall(struct.pack('>I', len(serialized_data)))
                self.client_conn.sendall(serialized_data)
                lock.release()
            except:
                pass
            time.sleep(3)

    def log_auth(self, lock):
        data_to_server = {'name_id': self.config['client']['name_id'], 'log_auth': []}
        serialized_data = pickle.dumps(data_to_server)
        try:
            lock.acquire()
            self.client_conn.sendall(struct.pack('>I', len(serialized_data)))
            self.client_conn.sendall(serialized_data)

            try:
                data_size = struct.unpack('>I', self.client_conn.recv(4))[0]
                received_payload = b""
                reamining_payload_size = data_size
                while reamining_payload_size != 0:
                    received_payload += self.client_conn.recv(reamining_payload_size)
                    reamining_payload_size = data_size - len(received_payload)
                self.last_record = pickle.loads(received_payload)["last_record"]
            except Exception:
                pass
            lock.release()
        except Exception:
            pass
        while self.isAlive:
            time.sleep(5)
            data_to_server = {'name_id': self.config['client']['name_id']}
            data_to_server.update(sensors.Sensor.get_auth_log(self.last_record))
            serialized_data = pickle.dumps(data_to_server)
            try:
                lock.acquire()
                self.client_conn.sendall(struct.pack('>I', len(serialized_data)))
                self.client_conn.sendall(serialized_data)
                try:
                    data_size = struct.unpack('>I', self.client_conn.recv(4))[0]
                    received_payload = b""
                    reamining_payload_size = data_size
                    while reamining_payload_size != 0:
                        received_payload += self.client_conn.recv(reamining_payload_size)
                        reamining_payload_size = data_size - len(received_payload)
                    self.last_record = pickle.loads(received_payload)["last_record"]
                except Exception:
                    pass
                lock.release()
            except Exception:
                pass

    def run_jobs(self):

        if eval(self.config['sensors']['uptime']):
            uptime = threading.Thread(target=self.uptime, args=(self.lock,))
            uptime.start()

            #start_new_thread(self.uptime, (self.lock,))
        if eval(self.config['sensors']['log_auth']):
            start_new_thread(self.log_auth, (self.lock,))
        if eval(self.config['sensors']['disk_space']):
            start_new_thread(self.disk_space, (self.lock,))
        if eval(self.config['sensors']['smart']):
            start_new_thread(self.smart, (self.lock,))
        if eval(self.config['sensors']['hwm']):
            start_new_thread(self.hwm, (self.lock,))
        if eval(self.config['sensors']['services']):
            start_new_thread(self.services, (self.lock,))

    def main(self):

        try:
            self.client_conn.connect((self.config['client']['host'], int(self.config['client']['port'])))
        except:
            self.status_conn = True

        while self.isAlive:

            print("while")
            if self.status_conn:
                if self.lock.locked():
                    self.lock.release()
                try:
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.path + r"ssl\server.crt")
                    context.load_cert_chain(certfile=self.path + r"\ssl\client.crt", keyfile=self.path + r"\ssl\client.key")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5.0)
                    self.client_conn = context.wrap_socket(sock, server_side=False, server_hostname="LAServer")
                    self.client_conn.connect((self.config['client']['host'], int(self.config['client']['port'])))
                    self.status_conn = False
                except Exception:
                    pass
            else:
                if eval(self.config['sensors']['uptime']):
                    with self.lock:
                        if not self.threads['uptime']:
                            print("not run uptime")
                            uptime = threading.Thread(target=self.uptime, args=(self.lock, True))
                            uptime.start()
                            self.threads.update({'uptime': True})

            time.sleep(1)
        self.client_conn.close()

    def SvcDoRun(self):
        self.isAlive = True
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        logging.info('AgentLA start')
        self.main()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def SvcStop(self):
        self.isAlive = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        logging.info('AgentLA stop')
        win32event.SetEvent(self.hWaitStop)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(Agent)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(Agent)
