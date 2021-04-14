from flask import request, abort, make_response, jsonify
import logging
import requests
import hashlib
from datetime import datetime, timezone
import time
from requests.exceptions import HTTPError, ConnectTimeout, ReadTimeout, SSLError
import base64
from config.tsurls import TS_GEO_URL, TS_WEATHER_URL
from config.tsconfig import HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT

# initialize logger for app
logger = logging.getLogger(__name__)

# main function used for API endpoint /ts-main/route/{start_addr}/{end_addr}
def buildRoute(start_addr,end_addr):
    # create uniquie trans_id
    trans_id = buildTransId()

    # get optional vars
    start_time = validateDate(request.args.get('start',default='now'))
    # should come out as the following: YYYY-MM-DDTHH:MM:SSZ+0000
    # will be converted in to 15 minute segments.

    # clean input and log for debug mode
    logger.debug(f'[trans_id: {trans_id}, start_addr: {start_addr}')
    logger.debug(f'[trans_id: {trans_id}, end_addr: {end_addr}')
    clean_start_addr = cleanInput(start_addr)
    logger.debug(f'[trans_id: {trans_id}, clean_start_addr: {clean_start_addr}')
    clean_end_addr = cleanInput(end_addr)
    logger.debug(f'[trans_id: {trans_id}, clean_end_addr: {clean_end_addr}')

    # initialize message variable
    message = None

    # call /ts-geo/route
    message = call_ts_geo(clean_start_addr,clean_end_addr,trans_id)

    # grab weather data for geo_spacers
    weather_data = []
    pull_time = start_time
    for i in message['data']['geo_spacers']:
        weather_data.append(call_ts_weather(i[0],i[1],pull_time,trans_id))
        pull_time = pull_time + 3600 # add 1 hour to pull_time

    message['data']['weather_data'] = weather_data

    return message

def validateDate(date_string): #work in storing .tzinfo
    try:
        if date_string == 'now':
            if int(datetime.now().strftime("%M")) <= 30: # find a way to set a cookie for UTC offset of user
                # give current hour 
                return int(datetime.strptime(datetime.now().strftime("%Y-%m-%dT%H:00:00Z"),"%Y-%m-%dT%H:%M:%SZ").timestamp())
            else:
                # give next hour
                return int((datetime.strptime(datetime.now().strftime("%Y-%m-%dT%H:00:00Z"),"%Y-%m-%dT%H:%M:%SZ").timestamp()) + 3600)

        else: # add logic to check for times before now.
            input_time = datetime.strptime(date_string,"%Y-%m-%dT%H:%M:%SZ%z")
            input_time = input_time.replace(minute=0,second=0)
            return int(input_time.timestamp())
    except ValueError:
        return -1

def cleanInput(addr):
    return addr.strip().replace(" ","+")

def call_ts_geo(start_addr,end_addr,trans_id):
    message = {}
    message['status'] = 'EMPTY'
    if start_addr != "" and end_addr != "":
        full_url = f'{TS_GEO_URL}/{start_addr}/{end_addr}/{trans_id}'
        service = "/ts-geo/route"
        logger.info(f'Calling {service} API [trans_id: {trans_id}]')
        response = ''

        try:
            response = requests.get(url=full_url, timeout=(HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT))
        except HTTPError as http_err:
            logger.error(f'HTTP error occured on {service} [trans_id: {trans_id}]: {http_err}')
            eres = jsonify(status="ERROR", error_code="HTTP_ERROR", error_message="There was an HTTP_ERROR on the server side.")
            abort(make_response(eres,500))
        except SSLError as ssl_err:
            logger.error(f'SSL error occured on {service} [trans_id: {trans_id}]: {ssl_err}')
            eres = jsonify(status="ERROR", error_code="SSL_ERROR", error_message="There was an SSL_ERROR on the server side.")
            abort(make_response(eres,500))
        except ConnectTimeout as ct:
            logger.error(f'Connection Timeout occured on {service} [trans_id: {trans_id}]: {ct}')
            eres = jsonify(status="ERROR", error_code="HTTP_CONNECT_TIMEOUT", error_message="The server was unable to make an HTTP connection.")
            abort(make_response(eres,500))
        except ReadTimeout as rt:
            logger.error(f'Read Timeout occured on {service} [trans_id: {trans_id}]: {rt}')
            eres = jsonify(status="ERROR", error_code="HTTP_READ_TIMEOUT", error_message="The server took too long to respond.")
            abort(make_response(eres,500))
        except Exception as err:
            logger.error(f'Error occured on {service} [trans_id: {trans_id}]: {err}')
            eres = jsonify(status="ERROR", error_code="UNKNOWN_ERROR", error_message="An unknown error occured on the server side.")
            abort(make_response(eres,500))
        else:
            if response.status_code == 200:
                message = response.json()
                logger.info(f'[trans_id: {trans_id}, status: {message["status"]}]')

    return message

def call_ts_weather(lat,lon,pull_time,trans_id):
    message = {}
    message['status'] = 'EMPTY'
    full_url = f'{TS_WEATHER_URL}/{lat}/{lon}/{pull_time}/{trans_id}'
    service = "/ts-weather/routeForecast"
    logger.info(f'Calling {service} API [trans_id: {trans_id}]')

    response = ''

    try:
        response = requests.get(url=full_url, timeout=(HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT))
    except HTTPError as http_err:
        logger.error(f'HTTP error occured on {service} [trans_id: {trans_id}]: {http_err}')
        eres = jsonify(status="ERROR", error_code="HTTP_ERROR", error_message="There was an HTTP_ERROR on the server side.")
        abort(make_response(eres,500))
    except SSLError as ssl_err:
        logger.error(f'SSL error occured on {service} [trans_id: {trans_id}]: {ssl_err}')
        eres = jsonify(status="ERROR", error_code="SSL_ERROR", error_message="There was an SSL_ERROR on the server side.")
        abort(make_response(eres,500))
    except ConnectTimeout as ct:
        logger.error(f'Connection Timeout occured on {service} [trans_id: {trans_id}]: {ct}')
        eres = jsonify(status="ERROR", error_code="HTTP_CONNECT_TIMEOUT", error_message="The server was unable to make an HTTP connection.")
        abort(make_response(eres,500))
    except ReadTimeout as rt:
        logger.error(f'Read Timeout occured on {service} [trans_id: {trans_id}]: {rt}')
        eres = jsonify(status="ERROR", error_code="HTTP_READ_TIMEOUT", error_message="The server took too long to respond.")
        abort(make_response(eres,500))
    except Exception as err:
        logger.error(f'Error occured on {service} [trans_id: {trans_id}]: {err}')
        eres = jsonify(status="ERROR", error_code="UNKNOWN_ERROR", error_message="An unknown error occured on the server side.")
        abort(make_response(eres,500))
    else:
        if response.status_code == 200:
            message = response.json()
            logger.info(f'[trans_id: {trans_id}, status: {message["status"]}]')

    return message

def parseWeatherData(tmp_data, trans_id):
    weather_data = []
    # for i in tmp_data:
    #     if i['status'] != 'OK':
    #         check_good = False
    #         logger.error(f'There was a bad response sent back from /ts-weather/routeForcast API [trans_id: {trans_id}]')
    #         break
    #
    count = 0
    for i in tmp_data:
        build_data = {}
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
