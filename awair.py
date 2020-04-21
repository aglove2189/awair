import functools
import datetime
from collections import defaultdict
import requests
import pandas as pd


class Awair:
    def __init__(self, api):
        self.api = api
        self.headers = {"Authorization": f"Bearer {self.api}"}
        self.base_url = "https://developer-apis.awair.is/v1/users/self/devices"

    @functools.lru_cache()
    def get_devices(self):
        r = requests.request("GET", self.base_url, headers=self.headers, data={})
        return r.json()["devices"]

    def get_api_usage(self, device):
        device_type = device["deviceType"]
        device_id = device["deviceId"]
        url = f"{self.base_url}/{device_type}/{device_id}/api-usages"
        r = requests.request("GET", url, headers=self.headers, data={})
        return r.json()

    def get_sensor_data(self, from_date, to_date, device=None):
        if device is None:
            device = self.get_devices()[0]
        if type(from_date) == datetime.date:
            from_date = from_date.isoformat()
        if type(to_date) == datetime.date:
            to_date = to_date.isoformat()

        device_type = device["deviceType"]
        device_id = device["deviceId"]
        url = f"{self.base_url}/{device_type}/{device_id}/air-data/15-min-avg?fahrenheit=True&from={from_date}&to={to_date}"
        r = requests.request("GET", url, headers=self.headers, data={})
        if r.ok:
            return r.json()["data"]
        else:
            raise ValueError(r)

    def get_sensor_df(self, from_date, to_date, device=None):
        data = self.get_sensor_data(from_date, to_date, device)
        sensor_data = defaultdict(list)
        for i in data:
            sensors = i["sensors"]
            for j in sensors:
                sensor_data[j['comp']].append(j['value'])

        df = pd.DataFrame.from_dict(data)
        sensor_df = pd.DataFrame.from_dict(sensor_data, orient='index').transpose()

        return df.join(sensor_df).drop(['sensors', 'indices'], axis=1, errors='ignore')
