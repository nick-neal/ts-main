from flask import request, abort, make_response, jsonify
import requests
from requests.exceptions import HTTPError, ConnectTimeout, ReadTimeout, SSLError
import datetime
import hashlib
import logging
from config.tsurls import GOOGLE_URL
from config.tskeys import G_PLACES_API_KEY
from config.tsconfig import HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT

# initialize logger for app
logger = logging.getLogger(__name__)

# main function used for API endpoint /ts-main/address/autocomplete/{addr}
def autocomplete(addr):
    sess = buildSession()

    logger.debug(f'[addr: {addr}] [session: {sess}]')

    clean_addr = cleanInput(addr)
    logger.debug(f'[clean_addr: {clean_addr}] [session: {sess}]')

    res = callAutocompleteAPI(clean_addr,sess)
    if res['status'] == 'OK':
        message = {"addr":clean_addr, "session":sess, "status":res['status'], "addresses":res['addresses']}
    else:
        message = {"addr":clean_addr, "session":sess, "status":res['status']}

    logger.debug(f'[message: {message}] [session: {sess}]')

    return message

def cleanInput(addr):
    return addr.strip().replace(" ","+")#.replace("&","%26").replace("=","%3D")

def callAutocompleteAPI(addr,sess):
    message = {"status":"EMPTY_ADDR"}
    if addr != "":
        # find way to restrict US address lookup.
        guri = f"/maps/api/place/autocomplete/json?input={addr}&key={G_PLACES_API_KEY}&sessiontoken={sess}"
        full_url = f'{GOOGLE_URL}{guri}'
        service = '/maps/api/place/autocomplete'
        logger.info(f'Calling {service} API [session: {sess}]')
        response = ''

        try:
            response = requests.get(url=full_url,timeout=(HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT))
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
        else :
            if response.status_code == 200:
                jres = response.json()
                message['status'] = jres['status']
                logger.info(f'[session: {sess}, status: {jres["status"]}]')

                if jres['status'] == 'OK':
                    message['addresses'] = parseJsonResponse(jres)

    return message

def parseJsonResponse(jres):
    res_addr = []
    for jobj in jres['predictions']:
        res_addr.append(jobj['description'])

    return res_addr

def buildSession():

    # build well defined session handler.

    ip_addr = request.remote_addr
    minute = int((datetime.datetime.now()).strftime("%M"))
    dt = (datetime.datetime.now()).strftime("%d%m%Y%H")
    convstr = ""
    if minute >= 0 and minute < 10:
        convstr = f'{ip_addr}{dt}0'
    elif minute >= 10 and minute < 20:
        convstr = f'{ip_addr}{dt}1'
    elif minute >= 20 and minute < 30:
        convstr = f'{ip_addr}{dt}2'
    elif minute >= 30 and minute < 40:
        convstr = f'{ip_addr}{dt}3'
    elif minute >= 40 and minute < 50:
        convstr = f'{ip_addr}{dt}4'
    elif minute >= 50 and minute < 60:
        convstr = f'{ip_addr}{dt}5'

    return (hashlib.md5(convstr.encode()).hexdigest())
