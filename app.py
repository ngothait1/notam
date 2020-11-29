import asyncio

import utils
import config
import json
import logging
from aiohttp import web


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
NOTAM_DICT = {}


routes = web.RouteTableDef()


def get_natam_location(notam):
    output = []
    isSkipWord = False
    notamAsList = notam.split()
    for index, word in enumerate(notamAsList):
        if isSkipWord:
            isSkipWord = False
            continue
        try:
            if utils.is_digital_and_letters(word):
                if word.startswith("N"):
                    word = word.lstrip("N")
                    if "E" in word:
                        splitByE = word.split("E")
                        north = splitByE[0].strip()
                        east  = splitByE[1].strip()
                        output.append(utils.get_coordinates(north, east))
                    else:
                        if index < len(notamAsList):
                            nextWord = notamAsList[index + 1]
                            if utils.is_digital_and_letters(nextWord) and nextWord.startswith("E"):
                                north = word
                                east  = nextWord.lstrip("E")
                                output.append(utils.get_coordinates(north, east))
                                isSkipWord = True
                elif word.endswith("N"):
                    word = word.rstrip("N")
                    if index < len(notamAsList):
                        nextWord = notamAsList[index + 1]
                        if utils.is_digital_and_letters(nextWord) and nextWord.endswith("E"):
                            north = word
                            east = nextWord.rstrip("E")
                            output.append(utils.get_coordinates(north, east))
                            isSkipWord = True

        except Exception as e:
            print(e)
            return None
    return output


def build_google_maps_url(notam):
    locationsList = get_natam_location(notam)
    if not locationsList:
        return None
    return "https://www.google.com/maps/dir/" + "/".join(
        [location for location in locationsList])


async def get_notam_data():
    airports_data = []
    asyncTasks    = []
    for airport in config.AIRPORTS:
        try:
            asyncTasks.append(asyncio.create_task(utils.get_html_content(config.AIRPORT_URL.format(airport))))
        except Exception as err:
            logger.exception(f'Failed to get notam data [url]: {config.AIRPORT_URL.format(airport)} [err]: {err}')
    for index, task in enumerate(asyncTasks):
        await task
        airports_data.append(task.result())
        logger.info("Appending data from " + config.AIRPORTS[index])
    return airports_data


async def get_notam_dict():
    output = {}
    data = await get_notam_data()
    for index, airportJson in enumerate(data):
        totalRows   = airportJson['total']
        if totalRows > 0:
            airportDict = {'num_of_msgs': totalRows, 'type_a': [], 'type_c': []}
            for notam in airportJson['rows']:
                notamDict = {}
                type                  = notam['series']
                notamDict['msg']      = notam['iteme']
                notamDict['modified'] = int(notam['modified'])
                googleMapsUrl = build_google_maps_url(notam['iteme'])
                if googleMapsUrl:
                    notamDict['maps_url'] = googleMapsUrl
                if type.strip().upper() == 'C':
                    airportDict['type_c'].append(notamDict)
                else:
                    airportDict['type_a'].append(notamDict)
            airportDict['num_of_type_a'] = len(airportDict['type_a'])
            airportDict['num_of_type_c'] = len(airportDict['type_c'])
            output[config.AIRPORTS[index]] = airportDict
    return output


@routes.get('/{airport}/{notam_type}')
async def get_notam_airport_data(request) -> web.Response:
    try:
        airport   = request.match_info.get('airport').upper()
        notamType = "type_" + request.match_info.get('notam_type').lower()
        logger.info("Got request to retrieve notam data for airport " + airport + " " + notamType)
        responseText = json.dumps(NOTAM_DICT[airport][notamType])
        logger.info(responseText)
    except Exception as e:
        responseText = ""
        logger.exception(e)
    return web.Response(text=json.dumps(responseText))

@routes.get('/')
async def get_notam_airports(request) -> web.Response:
    global NOTAM_DICT
    logger.info("Got request to retrieve notam data")
    NOTAM_DICT = await get_notam_dict()
    response = {}
    for key in NOTAM_DICT.keys():
        response[key] = {}
        response[key]['num_of_type_a'] = NOTAM_DICT[key]['num_of_type_a']
        response[key]['num_of_type_c'] = NOTAM_DICT[key]['num_of_type_c']

    logger.info(f'notam data: {response}')
    return web.Response(text=json.dumps(response))



app = web.Application()
app.add_routes(routes)
web.run_app(app, port=5001, host='127.0.0.1')

# Frontend:
    # react
    # angular
    # viewjs
#
#
# backend server iohttp