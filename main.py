import requests
import json
import os
import logging
import time

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.INFO)
SLEEP_SECONDS = 60 * 11


def get_us_infections():
    params = {
        'f': 'json',
        'where': "(Confirmed > 0) AND (Country_Region='US')",
        'returnGeometry': 'false',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'outStatistics': '[{"statisticType":"sum","onStatisticField":"Confirmed","outStatisticFieldName":"value"}]',
        'outSR': '102100',
        'cacheHint': 'true'
    }
    r = requests.get(
        'https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/1/query',
        headers={
            "Referer": "https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Sec-Fetch-Dest": "empty"
        },
        params=params
    )
    return r.json()["features"][0]['attributes']['value']


def get_non_china_infections():
    params = {
        'f': 'json',
        'where': "1=1",
        'returnGeometry': 'false',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'orderByFields': 'Report_Date_String desc',
        'resultOffset': '0',
        'resultRecordCount': '1',
        'cacheHint': 'true'
    }
    r = requests.get(
        'https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/cases_time_v3/FeatureServer/0/query',
        headers={
            "Referer": "https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Sec-Fetch-Dest": "empty"
        },
        params=params
    )
    return r.json()['features'][0]['attributes']['Other_Locations']


def say_it(message):
    logging.info(message)
    os.system("say {}".format(
        message
    ))


if __name__ == "__main__":
    logging.info("I'll let you know when more cases are reported.")
    while True:
        with open('data.json', 'r') as file:
            data_store = json.loads(file.read())

        us_infections = get_us_infections()
        non_china_infections = get_non_china_infections()
        said_something = False

        if us_infections > data_store['us_infections']:
            new_cases = us_infections - data_store['us_infections']
            say_it("Confirmed coronavirus infections in the United States have increased by {} cases.".format(
                new_cases
            ))
            said_something = True
        if non_china_infections > data_store['non_china_infections']:
            new_cases = non_china_infections - data_store['non_china_infections']
            say_it("Confirmed worldwide coronavirus infections outside of China have increased by {} cases.".format(
                new_cases
            ))
            said_something = True
        if said_something:
            logging.info("Re-entering the {} second poll loop. I'll let you know when more cases are reported.".format(
                SLEEP_SECONDS
            ))
            logging.info("Data source: https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6")

        data_store['us_infections'] = us_infections
        data_store['non_china_infections'] = non_china_infections
        with open('data.json', 'w') as writer:
            writer.write(json.dumps(data_store))

        time.sleep(SLEEP_SECONDS)
