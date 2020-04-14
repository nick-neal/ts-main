from flask import request
import logging
import requests
import hashlib
from requests.exceptions import HTTPError
import base64

# initialize logger for app
logger = logging.getLogger(__name__)

#set constants
TS_GEO_URL='http://localhost:4081/ts-geo/route'
TS_WEATHER_URL='http://localhost:4082/ts-weather/grabRouteForcast'

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
    logger.debug(f'[trans_id: {trans_id}, clean_start_addr: {clean_end_addr}')

    # call /ts-geo/route
    message = call_ts_geo(clean_start_addr,clean_end_addr,trans_id)

    # if status = ok, cal /ts-weather/grabRouteForcast post
    weather_data = {}
    if message['status'] == 'OK':
        weather_data = call_ts_weather(message['data']['geo_spacers'],trans_id)
    else:


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

def call_ts_weather(geo_list,trans_id):
    return True

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def buildTransId():
    # build well defined session handler.

    ip_addr = request.remote_addr
    minute = int((datetime.datetime.now()).strftime("%M"))
    dt = (datetime.datetime.now()).strftime("%d%m%Y%H%M%S%f")
    convstr = f'{ip_addr}{dt}'

    return (hashlib.sha256(convstr.encode()).hexdigest())
