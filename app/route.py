from flask import request
import logging
import requests
import hashlib
import datetime
from requests.exceptions import HTTPError
import base64

# initialize logger for app
logger = logging.getLogger(__name__)

#set constants
TS_GEO_URL='http://172.17.0.3:4081/ts-geo/route'
TS_WEATHER_URL='http://172.17.0.4:4082/ts-weather/routeForcast'

# main function used for API endpoint /ts-main/route/{start_addr}/{end_addr}
def buildRoute(start_addr,end_addr):
    # create uniquie trans_id
    trans_id = buildTransId()

    # clean input and log for debug mode
    logger.debug(f'[trans_id: {trans_id}, start_addr: {start_addr}')
    logger.debug(f'[trans_id: {trans_id}, end_addr: {end_addr}')
    clean_start_addr = cleanInput(start_addr)
    logger.debug(f'[trans_id: {trans_id}, clean_start_addr: {clean_start_addr}')
    clean_end_addr = cleanInput(end_addr)
    logger.debug(f'[trans_id: {trans_id}, clean_end_addr: {clean_end_addr}')

    # call /ts-geo/route
    message = call_ts_geo(clean_start_addr,clean_end_addr,trans_id)

    # if status = ok, cal /ts-weather/grabRouteForcast post

    #message['data']['weather_data'] = []
    tmp_weather = []
    if message['status'] == 'OK':
        for i in message['data']['geo_spacers']:
            tmp_weather.append(call_ts_weather(i[0],i[1],trans_id))
        weather_data['data']['weather_data'] = parseWeatherData(tmp_weather, trans_id)
    else:
        logger.error(f'There was an issue retrieving data from /ts-geo/route API [trans_id: {trans_id}]')

    return message

def cleanInput(addr):
    return addr.strip().replace(" ","+")

def call_ts_geo(start_addr,end_addr,trans_id):
    message = {}
    message['status'] = 'EMPTY'
    if start_addr != "" and end_addr != "":
        full_url = f'{TS_GEO_URL}/{start_addr}/{end_addr}/{trans_id}'

        logger.info(f'Calling /ts-geo/route API [trans_id: {trans_id}]')
        response = ''

        try:
            response = requests.get(full_url)
        except HTTPError as http_err:
            logger.error(f'HTTP error occured for [trans_id: {trans_id}]: {http_err}')
            message['status'] = "HTTP_ERROR"
        except Exception as err:
            logger.error(f'Error occured for [trans_id: {trans_id}]: {err}')
            message['status'] = "UNKNOWN_ERROR"
        else:
            if response.status_code == 200:
                message = response.json()
                logger.info(f'[trans_id: {trans_id}, status: {message["status"]}]')

    return message

def call_ts_weather(lat,lon,trans_id):
    message = {}
    message['status'] = 'EMPTY'
    full_url = f'{TS_WEATHER_URL}/{lat}/{lon}/{trans_id}'

    logger.info(f'Calling /ts-weather/routeForecast API [trans_id: {trans_id}]')
    #b64_geo_list = stringToBase64(geo_list)

    '''
    data = {'geo_list': b64_geo_list,
            'trans_id': trans_id
            }
    '''
    response = ''

    try:
        response = requests.get(url=full_url)
    except HTTPError as http_err:
        logger.error(f'HTTP error occured for [trans_id: {trans_id}]: {http_err}')
        message['status'] = "HTTP_ERROR"
    except Exception as err:
        logger.error(f'Error occured for [trans_id: {trans_id}]: {err}')
        message['status'] = "UNKNOWN_ERROR"
    else:
        if response.status_code == 200:
            message = response.json()
            logger.info(f'[trans_id: {trans_id}, status: {message["status"]}]')

    return message

def parseWeatherData(tmp_data, trans_id):
    check_good = True
    weather_data = []
    for i in tmp_data:
        if i['status'] != 'OK':
            check_good = False
            logger.error(f'There was a bad response sent back from /ts-weather/routeForcast API [trans_id: {trans_id}]')
            break

    if check_good:
        count = 0
        for i in tmp_data:
            build_data = {}
            build_data['alerts'] = i['alerts']
            build_data['latitude'] = i['latitude']
            build_data['longitude'] = i['longitude']
            build_data['timezone'] = i['timezone']
            build_data['weather_data'] = i['weather_data'][count]

            weather_data.append(build_data)
            count += 1

    return weather_data

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def buildTransId():
    # build well defined session handler.

    ip_addr = request.remote_addr
    minute = int((datetime.datetime.now()).strftime("%M"))
    dt = (datetime.datetime.now()).strftime("%d%m%Y%H%M%S%f")
    convstr = f'{ip_addr}{dt}'

    return (hashlib.sha256(convstr.encode()).hexdigest())
