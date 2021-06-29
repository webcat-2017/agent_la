import clr
from datetime import datetime, timedelta
import ctypes
import math
import psutil
import winreg as reg
import subprocess
import re
import json


class Sensor(object):
    @staticmethod
    def __get_path():
        with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\AgentLA") as h:
            path = reg.EnumValue(h, 3)[1].strip("la_service.exe")
            #path = r"D:\myApp\AgentLA\\"

            return path

    @staticmethod
    def get_uptime():

        """
        @return: uptime system
        """
        sensors = dict()
        lib = ctypes.windll.kernel32
        t = lib.GetTickCount64()
        t = int(str(t)[:-3])
        mins, sec = divmod(t, 60)
        hour, mins = divmod(mins, 60)
        days, hour = divmod(hour, 24)
        sensors['uptime'] = [{"days": str(days), "hours": str(hour), "minutes": str(mins), "secounds": str(sec)}]
        return sensors

    @staticmethod
    def get_disk_space():

        """
        @return: disk usage space
        """
        sensors = dict()

        def convert_size(size_bytes):
            if size_bytes == 0:
                return "0B"
            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return "%s %s" % (s, size_name[i])

        disks = psutil.disk_partitions()
        parts = []

        for disk in disks:
            d = psutil.disk_usage(disk.mountpoint)
            parts.append(
                {'part': disk.device[:1], 'total': convert_size(d.total), 'used': convert_size(d.used),
                 'free': convert_size(d.free)})
        sensors['disk_space'] = parts
        return sensors

    @classmethod
    def get_smart(cls):
        """
        @return: smart disk
        """
        path = cls.__get_path()

        proc = subprocess.Popen(["%ssmartctl.exe" % path, "--scan"], shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out = proc.communicate()[0]
        dev_list = out.decode("utf-8").split("\r\n")
        disks = []
        for dev in dev_list:
            x = re.match('/\w+/\w+', dev)
            if x:
                disks.append(x.group())

        smart = {'smart': []}
        for disk in disks:
            proc = subprocess.Popen(['%ssmartctl.exe' % path, '-j', '-a', disk], shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out, err = proc.communicate()
            str_smart = out.decode("utf-8")
            smart['smart'].append(json.loads(str_smart))
        return smart

    @classmethod
    def get_hwm(cls):
        """
        @return: Temperature, load cpu etc, vbat and name hardware.
        """
        path = cls.__get_path()
        sensortypes = ['Voltage', 'Clock', 'Temperature', 'Load', 'Fan', 'Flow', 'Control', 'Level', 'Factor', 'Power',
                       'Data', 'SmallData']
        hardwaretypes = ['Mainboard', 'SuperIO', 'CPU', 'RAM', 'GpuNvidia', 'GpuAti', 'TBalancer', 'Heatmaster', 'HDD']

        file = path + 'OpenHardwareMonitorLib.dll'

        clr.AddReference(file)

        from OpenHardwareMonitor import Hardware

        handle = Hardware.Computer()
        handle.MainboardEnabled = True
        handle.CPUEnabled = True
        handle.RAMEnabled = True
        handle.GPUEnabled = True
        handle.HDDEnabled = True
        handle.Open()
        sensors = {'temperature': [], 'load': [], 'voltages': [], 'hardware': []}

        def parse_sensor(sensor, sensors):

            if sensor.SensorType == sensortypes.index('Temperature'):
                sensors['temperature'].append(
                    {hardwaretypes[sensor.Hardware.HardwareType] + " " + sensor.Hardware.Name: sensor.Value})
            elif sensor.SensorType == sensortypes.index('Load'):
                sensors['load'].append(
                    {hardwaretypes[sensor.Hardware.HardwareType] + " " + sensor.Hardware.Name: sensor.Value})
            elif sensor.SensorType == sensortypes.index('Voltage'):
                sensors['voltages'].append({sensor.Name: sensor.Value})

        for i in handle.Hardware:
            sensors['hardware'].append({hardwaretypes[i.HardwareType]: i.Name})
            i.Update()
            for sensor in i.Sensors:
                parse_sensor(sensor, sensors)
            for j in i.SubHardware:
                j.Update()
                for subsensor in j.Sensors:
                    parse_sensor(subsensor, sensors)
        sensors = {'hwm': sensors}
        return sensors

    @staticmethod
    def get_services():
        """
        :return: services list
        """
        services = list(psutil.win_service_iter())
        sensors = {'services': []}

        for service in services:
            serv_dict = service.as_dict()
            del serv_dict['description']
            sensors['services'].append(serv_dict)

        return sensors

    @staticmethod
    def get_auth_log(lr):

        """
        Get the event logs security
        """
        from winevt import EventLog
        global last_record
        last_record = lr
        data = {'log_auth': []}
        events = EventLog.Query("Security", "Event/System[EventRecordID>%s]" % last_record)

        for event in events:
            date = datetime.strptime(event.System.TimeCreated['SystemTime'][:-9], '%Y-%m-%dT%H:%M:%S')
            if event.EventID == 4625:
                time = str(date + timedelta(hours=3))
                event_id = event.System.EventID.cdata
                record = int(event.System.EventRecordID.cdata)
                user = event.EventData.Data[5].cdata
                address = event.EventData.Data[19].cdata
                hostname = event.EventData.Data[13].cdata
                point = int(event.EventData.Data[10].cdata)
                domain = event.EventData.Data[6].cdata

                if record > last_record:
                    data['log_auth'].append({
                        'time': time,
                        'event_id': event_id,
                        'record': record,
                        'user': user,
                        'address': address,
                        'hostname': hostname,
                        'point': point,
                        'domain': domain})

            if event.EventID == 4624:
                time = str(date + timedelta(hours=3))
                event_id = event.System.EventID.cdata
                record = int(event.System.EventRecordID.cdata)
                user = event.EventData.Data[5].cdata
                address = event.EventData.Data[18].cdata
                hostname = event.EventData.Data[11].cdata
                point = int(event.EventData.Data[8].cdata)
                domain = event.EventData.Data[6].cdata

                if record > last_record:
                    data['log_auth'].append({
                        'time': time,
                        'event_id': event_id,
                        'record': record,
                        'user': user,
                        'address': address,
                        'hostname': hostname,
                        'point': point,
                        'domain': domain})

        return data
