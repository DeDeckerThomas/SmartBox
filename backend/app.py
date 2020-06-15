# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading
import os
import subprocess
import signal

from RPi import GPIO
from models.DS18B20 import DS18B20
from models.DHT22 import DHT22
from models.HCSR05 import HCSR05
from models.LCD import LCD
from models.Alarm import Alarm
from models.AlarmHandler import AlarmHandler
from models.Ledstrip import Ledstrip


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


app = Flask(__name__)
# app.config['SECRET_KEY'] = 'Secret'

mac = 'Your mac address :D'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
CORS(app)


def measurements():
    temperature_sensor = DS18B20('28-00000c1d7d30')
    humidity_sensor = DHT22(16)
    while True:
        temperature = round(temperature_sensor.get_temperature(), 2)
        humidity = round(humidity_sensor.get_humidity(), 2)
        DataRepository.add_measurement(1, temperature)
        DataRepository.add_measurement(2, humidity)
        check_values = DataRepository.get_settings_by_userid(1)
        if check_values['MinTemp'] > temperature:
            DataRepository.post_notification(
                'Temperature is too low. Please turn on the heat.', 1)
        elif check_values['MaxTemp'] < temperature:
            DataRepository.post_notification(
                'Temperature is too high. Please turn on the airco.', 1)
        elif check_values['MinHum'] > humidity:
            DataRepository.post_notification(
                'Humidity is too low. Please open your window.', 1)
        elif check_values['MaxHum'] < humidity:
            DataRepository.post_notification(
                'Humidity is too high. Please open your window.', 1)
        socketio.emit('temperature', {'Value': temperature})
        socketio.emit('humidity', {'Value': humidity})
        time.sleep(60)


t1 = threading.Thread(target=measurements)
t1.start()


ledstrip = Ledstrip(mac)

active_alarms = []

lcd = LCD(25, 12, [17, 27, 22, 5, 6, 13, 23, 24])
lcd.start()

ultrasonic_sensor = HCSR05(20, 26)
alarmhandler = AlarmHandler(ultrasonic_sensor)

alarms = DataRepository.get_active_alarms_by_userid(1)
active_alarms = [Alarm(alarm['AlarmID'], alarm['UserID'], alarm['Name'],
                       alarm['IsActive'], str(alarm['StartTime']), alarm['Duration'], ultrasonic_sensor, alarmhandler) for alarm in alarms]

for alarm in active_alarms:
    alarm.start()
print(active_alarms)


# API ENDPOINTS
endpoint = '/api/v1/'


@app.route('/')
def hallo():
    return "Server is running."


@app.route(endpoint+'users/<userid>/settings/', methods=['GET', 'PUT'])
def get_settings_of_user(userid):
    if request.method == "GET":
        data = DataRepository.get_settings_by_userid(userid)
        return jsonify(data), 200
    elif request.method == "PUT":
        js = request.get_json()
        update_settings = DataRepository.update_settings(
            js['userid'], True, js['mintemp'], js['maxtemp'], js['minhum'], js['maxhum'])
        return jsonify(update_settings), 201


@app.route(endpoint + 'users/<userid>/devices/')
def get_devices(userid):
    data = DataRepository.get_devices_by_userid(userid)
    return jsonify(data), 200


@app.route(endpoint + 'users/<userid>/devices/<deviceid>', methods=['GET', 'PUT'])
def get_device(userid, deviceid):
    if request.method == "GET":
        data = DataRepository.get_device(deviceid)
        return jsonify(data), 200
    elif request.method == "PUT":
        js = request.get_json()
        data = DataRepository.update_device(
            deviceid, js['type'], js['color'], js['pattern'])
        if js['type'] == "color":
            color = js['color'].lstrip('#')
            color = list(int(color[i:i + 2], 16) for i in (0, 2, 4))
            ledstrip.send_color(color[0], color[1], color[2], 1)
        elif js['type'] == "pattern":
            print(js['pattern'])
            ledstrip.send_pattern(js['pattern'].upper())
        return jsonify(data), 201


@app.route(endpoint + 'users/<userid>/notifications/')
def get_notifications(userid):
    data = DataRepository.get_notifications_by_userid(userid)
    return jsonify(data), 200


@app.route(endpoint + 'sensors/')
def get_sensors():
    data = DataRepository.get_sensors()
    return jsonify(data), 200


@app.route(endpoint + 'sensors/<sensorid>/')
def get_sensor(sensorid):
    data = DataRepository.get_sensor_by_sensorid(sensorid)
    return jsonify(data), 200


@app.route(endpoint + 'sensors/history/')
def get_history():
    data = DataRepository.get_sensorhistory()
    return jsonify(data), 200


@app.route(endpoint + 'sensors/<sensorid>/history/')
def get_history_of_one_sensor(sensorid):
    data = DataRepository.get_sensorhistory_by_sensorid(sensorid)
    return jsonify(data), 200


@app.route(endpoint + 'users/<userid>/alarms/', methods=['GET', 'POST'])
def get_alarms(userid):
    if request.method == 'GET':
        data = DataRepository.get_alarms_by_userid(userid)
        return jsonify(data), 200
    elif request.method == 'POST':
        js = request.get_json()
        data = DataRepository.post_alarm(
            userid, js['name'], js['starttime'], js['duration'], js['days'])
        return jsonify(data), 201


@app.route(endpoint + 'users/<userid>/alarms/<alarmid>', methods=['GET', 'PUT', 'DELETE'])
def get_alarm_by_id(userid, alarmid):
    if request.method == "GET":
        data = DataRepository.get_alarm_by_userid(userid, alarmid)
        return jsonify(data), 200
    elif request.method == "PUT":
        js = request.get_json()
        data = DataRepository.update_alarm(
            userid, alarmid, js['name'], js['starttime'], js['duration'], js['days'])
        return jsonify(data), 201
    elif request.method == "DELETE":
        data = DataRepository.delete_alarm(alarmid, userid)
        return jsonify(data), 201


@app.route(endpoint + 'users/<userid>/alarms/<alarmid>/update', methods=['PUT'])
def update_alarm(userid, alarmid):
    if request.method == "PUT":
        js = request.get_json()
        data = DataRepository.update_alarm_status(
            js['status'], userid, alarmid)
        if js['status']:
            active = DataRepository.get_alarm_by_userid(userid, alarmid)
            alarm = Alarm(active['AlarmID'], active['UserID'], active['Name'], active['IsActive'], str(
                active['StartTime']), active['Duration'], ultrasonic_sensor, alarmhandler)
            active_alarms.append(alarm)
            alarm.start()
            print(active_alarms)
        else:
            for alarm in active_alarms:
                if alarm.alarm_id == int(alarmid):
                    alarm.isactive = False
                    active_alarms.remove(alarm)
                    del(alarm)
            print(active_alarms)
        return jsonify(data), 201


@app.route(endpoint+'users/<userid>/devices/<deviceid>/update', methods=['PUT'])
def update_ledstrip(userid, deviceid):
    if request.method == "PUT":
        js = request.get_json()
        print(js)
        data = DataRepository.update_ledstrip(
            userid, deviceid, js['status'], js['isactive'])
        if js['status']:
            lightdevice = DataRepository.get_device(deviceid)
            print(lightdevice)
            if int(lightdevice['PatternID']) == 1:
                color = lightdevice['Color'].lstrip('#')
                color = list(int(color[i:i + 2], 16) for i in (0, 2, 4))
                threading.Thread(target=ledstrip.send_color, args=(
                    color[0], color[1], color[2], 1)).start()
            else:
                threading.Thread(target=ledstrip.send_pattern, args=(
                    lightdevice['Pattern'].upper())).start()
        else:
            ledstrip.send_color(0, 0, 0, 1)
        return jsonify(data), 201


@app.route(endpoint+'poweroffpi/')
def poweroff():
    subprocess.Popen('sudo poweroff', stdout=subprocess.PIPE,
                     shell=True, preexec_fn=os.setsid)
    return jsonify(message='command executed successfully'), 200
# SOCKET IO


@ socketio.on('connect')
def init_connection():
    print('User connected')
    socketio.emit('temperature', DataRepository.get_latest_value(1))
    socketio.emit('distance', DataRepository.get_latest_value(3))
    socketio.emit('humidity', DataRepository.get_latest_value(2))


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
