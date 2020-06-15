from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def add_measurement(sensorid, value):
        sql = "INSERT INTO SensorHistory (SensorID, Value) VALUES (%s, %s);"
        params = [sensorid, value]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_sensorhistory_by_sensorid(sensorid):
        sql = "SELECT avg(Value) as Value,date_format(DATE(DateTime), '%m-%d-%Y') as Date FROM SmartBox.SensorHistory WHERE SensorID=%s GROUP BY date ORDER BY Date DESC LIMIT 10;"
        params = [sensorid]
        return Database.get_rows(sql, params)

    @staticmethod
    def get_sensorid_by_type(type):
        sql = "SELECT SensorID FROM Sensor WHERE Type = %s"
        params = [type]
        return Database.get_one_row(sql, params)['SensorID']

    @staticmethod
    def get_sensors():
        sql = "SELECT * FROM Sensor"
        return Database.get_rows(sql)

    @staticmethod
    def get_sensor_by_sensorid(sensorid):
        sql = "SELECT * FROM Sensor WHERE SensorID = %s"
        params = [sensorid]
        return Database.get_rows(sql, params)

    @staticmethod
    def get_sensorhistory():
        sql = "SELECT * FROM SensorHistory"
        return Database.get_rows(sql)

    @staticmethod
    def get_latest_value(sensorid):
        sql = "SELECT Value FROM SensorHistory WHERE SensorID = %s ORDER BY HistoryID DESC LIMIT 1"
        params = [sensorid]
        return Database.get_one_row(sql, params)

    @staticmethod
    def get_devices_by_userid(userid):
        sql = "SELECT * FROM LightDevice WHERE UserID = %s"
        params = [userid]
        return Database.get_rows(sql, params)

    @staticmethod
    def get_notifications_by_userid(userid):
        sql = "SELECT * FROM Notification WHERE UserID = %s ORDER BY NotificationID DESC LIMIT 3"
        params = [userid]
        return Database.get_rows(sql, params)

    @staticmethod
    def get_alarms_by_userid(userid):
        sql = "SELECT * FROM Alarm WHERE UserID = %s"
        params = [userid]
        data = Database.get_rows(sql, params)
        for alarm in data:
            alarm["StartTime"] = str(alarm["StartTime"])
            alarm["Duration"] = str(alarm["Duration"])
            sql_days = "SElECT Day.Name FROM SelectedDays JOIN Day USING(DayID) WHERE SelectedDays.AlarmID = %s"
            params_days = [alarm["AlarmID"]]
            alarm["Days"] = [day["Name"]
                             for day in Database.get_rows(sql_days, params_days)]
        return data

    @staticmethod
    def get_alarm_by_userid(userid, alarmid):
        sql = "SELECT * FROM Alarm WHERE UserID = %s AND AlarmID = %s"
        params = [userid, alarmid]
        sql_days = "SElECT Day.Name FROM SelectedDays JOIN Day USING(DayID) WHERE SelectedDays.AlarmID = %s"
        days_params = [alarmid]
        data = Database.get_one_row(sql, params)
        days = Database.get_rows(sql_days, days_params)
        data["StartTime"] = str(data["StartTime"])
        data["Duration"] = str(data["Duration"])
        data["Days"] = [day['Name'] for day in days]
        return data

    @staticmethod
    def get_active_alarms_by_userid(userid):
        sql = "SELECT * FROM Alarm WHERE IsActive = 1 AND UserID = %s"
        params = [userid]
        return Database.get_rows(sql, params)

    @staticmethod
    def get_settings_by_userid(userid):
        sql = "SELECT * FROM Settings WHERE UserID = %s"
        params = [userid]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_settings(userid, notifications_enabled, mintemp, maxtemp, minhum, maxhum):
        sql = "UPDATE Settings SET MinTemp = %s, MaxTemp = %s, MinHum=%s, MaxHum=%s  WHERE UserID = %s"
        params = [mintemp, maxtemp, minhum, maxhum, userid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def post_notification(message, userid):
        sql = "INSERT INTO Notification(Description, UserID) VALUES (%s,%s)"
        params = [message, userid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def post_alarm(userid, name, starttime, duration, days):
        dict_day = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
                    'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
        sql = "INSERT INTO Alarm(UserID, Name, StartTime, Duration) VALUES (%s,%s,%s,%s)"
        params = [userid, name, starttime, duration]
        data = Database.execute_sql(sql, params)
        alarmid = Database.get_one_row(
            "SElECT AlarmID FROM Alarm WHERE name=%s", [name])
        for day in days:
            Database.execute_sql(
                "INSERT INTO SelectedDays(AlarmID,DayID) VALUES(%s,%s)", [alarmid['AlarmID'], dict_day.get(day)])
        return data

    @staticmethod
    def update_alarm_status(status, userid, alarmid):
        sql = "UPDATE Alarm SET IsActive = %s WHERE AlarmID = %s AND UserID = %s"
        params = [status, alarmid, userid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_device(deviceid):
        sql = "SELECT * FROM LightDevice JOIN Pattern USING(PatternID) WHERE DeviceId = %s"
        params = [deviceid]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_device(deviceid, ptype, color, pattern):
        new_pattern = DataRepository.get_patternid_by_name(pattern)
        sql = "UPDATE LightDevice SET color=%s, PatternID = %s, Type=%s WHERE DeviceID =%s"
        params = [color, new_pattern['PatternID'], ptype, deviceid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_patternid_by_name(pattern):
        sql = "SELECT PatternID FROM Pattern WHERE Pattern = %s"
        params = [pattern]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_ledstrip(userid, deviceid, status, isactive):
        sql = "UPDATE LightDevice SET IsActive=%s, status=%s WHERE DeviceID =%s and UserID =%s"
        params = [isactive, status, deviceid, userid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_alarm(userid, alarmid, name, starttime, duration, days):
        dict_day = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
                    'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
        sql = "UPDATE Alarm SET Name=%s,StartTime=%s,Duration=%s WHERE alarmid =%s"
        params = [name, starttime, duration, alarmid]
        data = Database.execute_sql(sql, params)
        Database.execute_sql(
            'DELETE FROM SelectedDays WHERE AlarmID =%s', [alarmid])
        for day in days:
            Database.execute_sql(
                "INSERT INTO SelectedDays(AlarmID,DayID) VALUES(%s,%s)", [int(alarmid['AlarmID']), int(dict_day.get(day))])
        return data

    @ staticmethod
    def delete_alarm(alarmid, userid):
        sql= "DELETE FROM Alarm WHERE AlarmID = %s AND UserID = %s"
        params= [alarmid, userid]
        Database.execute_sql(
            "DELETE FROM SelectedDays WHERE AlarmID = %s", [alarmid])
        return Database.execute_sql(sql, params)
