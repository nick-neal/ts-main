from flask import request
import requests
from requests.exceptions import HTTPError
import datetime
import hashlib
import logging
from config.tsurls import GOOGLE_URL
from config.tskeys import G_PLACES_API_KEY

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
        logger.info(f'Calling /maps/api/place/autocomplete API [session: {sess}]')
        response = ''

        try:
            response = requests.get(full_url)

            response.raise_for_status()
        except HTTPError as http_err:
            logger.error(f'HTTP error occured for [session: {sess}]: {http_err}')
            message['status'] = "HTTP_ERROR"
        except Exception as err:
            logger.error(f'Error occured for [session: {sess}]: {err}')
            message['status'] = "UNKNOWN_ERROR"
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
