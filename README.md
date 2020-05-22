# ts-main

## Description

This is the main micro service that will handle client requests for TravelStorms. It is currently configured to run in docker for development purposes, but will soon include a kubernetes config for deploying to prod environments.

You will need to have ts-geo and ts-weather running to use ts-main, as it relies on the services to collect results for the client request.  

## setting up API KEYS
Due to security, you will need to create a new file: `app/config/tskeys.py`

add the following to the new file:

```
from config.tsconfig import APP_ENV

### API KEYS ###

if APP_ENV == "DEV":
    G_PLACES_API_KEY = '<Google Maps Places API Key>'

```

## Running in docker

**You will need docker installed on your computer to run the code**

you are going to need to `cd` in to the directory you have pulled the code to. Once you are there, go ahead and run the following commands based on your needs.

`make build`
This will build the docker container where you will run the code.

`make run`
This will run the container and allow you to interact with the API.

`make inspect`
**container must be running** This will allow you to open a shell in the container for viewing log files and debugging configurations.

`make stop`
This will stop the running container.

`make clean`
This will purge the docker registry of this container.

## API
For app name and version, query *http://127.0.0.1:4080/*

The api will be located at *http://127.0.0.1:4080/ts-main*

**In order for this API to function properly, you will need to also be running the ts-geo & ts-weather containers as well.**

### `/address/autocomplete/{addr} [GET]`

This route is used to autocomplete addresses typed in to an input box.

##### Request
Var Name | Var Type | Description
-------- | -------- | -----------
addr | String | This will be a string that can be sent, where you will receive address suggestions.

##### Response (json)
Var Name | Var Type | Description
-------- | -------- | -----------
addr | String | This is the address you sent.
addresses | String Array | This is a list of addresses that are suggested based on the addr that was sent by the client.
session | String | This string carries a unique session token on each request for logging and debugging purposes.
status | String | "OK" means the application was able to complete the request with no issues. any other response means an error occured, and the integrity of any data may be compromised.

```
/address/autocomplete/1600+Pennsylvania

{
  "addr": "1600+Pennsylvania",
  "addresses": [
    "1600 Pennsylvania Street, Denver, CO, USA",
    "1600 South Pennsylvania Street, Denver, CO, USA",
    "1600 Pennsylvania Avenue Northwest, Washington, DC, USA",
    "1600 Pennsylvania Avenue Southeast, Washington, DC, USA",
    "1600 Pennsylvania Avenue, Dallas, TX, USA"
  ],
  "session": "25c14cbf2f4823eb42a25a9d1912adb1",
  "status": "OK"
}
```

### `/route/{start_addr}/{end_addr} [GET]`

This is used to pull route direction data from google maps, and corresponding weather data.

##### Request

Var Name | Var Type | Description
-------- | -------- | -----------
start_addr | String | This is the starting address for your route.
end_addr | String | This is the destination address for your route.

##### Response (json)

Var Name | Var Type | Description
-------- | -------- | -----------
data | Object | This carries all geo-location and weather data.
data -> distance | int | This is the distance of the route measured in meters.
data -> duration | int | This is the time it would take to travel the route measured in seconds.
data -> geo_spacers | float arrays | These are geo-coordinate arrays along the route that weather data will be pulled for.
data -> polyline | String | This is an encoded string containing geo-coordinates that will draw the route line on a map.
data -> weather_data | Object Array | This is an array containing weather data from the geo-coordinates in the data -> geo_spacers array.
data -> weather_data -> [] -> alerts | Object Array | These are weather alerts for the area where weather data is pulled from. if there are no alerts, the value will be set to "EMPTY".
data -> weather_data -> [] -> alerts -> [] -> description | String | This will give a full description for the alert.
data -> weather_data -> [] -> alerts -> [] -> expires | int | This is when the alert is set to expire measured in a unix timestamp.
data -> weather_data -> [] -> alerts -> [] -> regions | String Array | These are the regions affected by the alert.
data -> weather_data -> [] -> alerts -> [] -> severity | String | This is the level of severity the alert has been given.
data -> weather_data -> [] -> alerts -> [] -> time | int | This is when the alert was put in to effect measured in a unix timestamp.
data -> weather_data -> [] -> alerts -> [] -> title | String | This is a short, formal description of the alert.
data -> weather_data -> [] -> alerts -> [] -> uri | String | This is the reference of where the alert data was retrieved from.
data -> weather_data -> [] -> latitude | float | This is the latitude where the weather data was pulled from.
data -> weather_data -> [] -> longitude | float | This is the longitude where the weather data was pulled from.
data -> weather_data -> [] -> timezone | String | This is the timezone of the geo-coordinates (**important:** time variables in this object are set to this timezone).
data -> weather_data -> [] -> weather_data | Object | This is where detailed weather data is stored.
data -> weather_data -> [] -> weather_data -> apparentTemperature | float | This is the temperature it feels like, measured in Fahrenheit.
data -> weather_data -> [] -> weather_data -> cloudCover | float | No Description.
data -> weather_data -> [] -> weather_data -> dewPoint | float | No Description.
data -> weather_data -> [] -> weather_data -> humidity | float | No Description.
data -> weather_data -> [] -> weather_data -> icon | String | This is issued to display a corresponding image icon.
data -> weather_data -> [] -> weather_data -> ozone | float | No Description.
data -> weather_data -> [] -> weather_data -> precipIntensity | float | No Description.
data -> weather_data -> [] -> weather_data -> precipProbability | float | No Description.
data -> weather_data -> [] -> weather_data -> pressure | float | No Description.
data -> weather_data -> [] -> weather_data -> summary | String | summarizes the forecast.
data -> weather_data -> [] -> weather_data -> temperature | float | This is the actual temperature measured in Fahrenheit.
data -> weather_data -> [] -> weather_data -> time | int | the time for the forecast measured in a unix timestamp. it is important to link this time with the timezone provided, or time may not display accurately.
data -> weather_data -> [] -> weather_data -> uvIndex | float | No Description.
data -> weather_data -> [] -> weather_data -> visibility | float | No Description.
data -> weather_data -> [] -> weather_data -> windBearing | float | No Description.
data -> weather_data -> [] -> weather_data -> windGust | float | No Description.
data -> weather_data -> [] -> weather_data -> windSpeed | float | No Description.
end_addr | String | This is the destination address for your route.
start_addr | String | This is the starting address for your route.
status | String | "OK" means the application was able to complete the request with no issues. any other response means an error occured, and the integrity of any data may be compromised.

```
/route/Denver,+CO/Grand+Junction,+CO

(response has been omitted due to it's size)

{
  "data": {
    "distance": 391649,
    "duration": 14598,
    "geo_spacers": [
      ...
      [
        39.66086,
        -105.9867
      ],
      [
        39.6728,
        -106.79992
      ],
      ...
    ],
    "polyline": "g}pqFlmx_Sdu@aBfTxC`@bTrJ~t@`GpOt@~nBq@`fD`An~Ow@ddHbo@bt@jcCnkBrBjgAoY`aCwV`wC_~@rcHjkAvxBiEvv@ak@|`AqVvrByJneB_AnhA}Yj{@as@lnBasAxw@eTf[nIla@`Ctz@cUfhAlMpyC`Yh_AsDt|@kFrgB_aA~pDkaArnDmJl{DjJ|yCrTv_Brj@rn@pm@vkBnm@fs@nmBj{@bdA|Jlt@haAlg@~nCuKnsCrGduElNl~A{Kv_Cqf@~{A{BtmBjp@`uBvgAtnArB|o@dO`dCvIfdC~Sn|ChZr}@ru@dfAlr@pdDvm@zkBxcA`pCdn@hkBl`@dNbi@IzYv`@zhAbnAjeA`|AtzA`o@va@p~@j}AnhAt~@zZ|]hOdc@gW|^iA`Zzb@veAmBt`@~HrJh{AgFhqAoQrhBZlr@qXhXmqAvhAkqANy|BbyAcvBvvBymAuTmd@|u@gShfBckAtl@osBdNyoAflC}_@zhCbYjwChD`{BkTxfBjVnnAhwAbmCpx@hsAv_@ty@|\\tY}G~u@{k@`]ka@tkCuaBtrFgLfu@lNjhAi]|yBmHx}AoUj`@gh@ttCwJndBcGh{@}_@tq@ioB|o@uJrh@sdAp{@sm@teCk{@ju@hB~iBj`@fvA|iAnxB|y@b_A|Ux`AjL~cAr`@heCheBvoEpK~zAzM`fHgKthChDv_EcSlgDdm@lqDdZtwCyYl{DnVb}B|s@|eB|[~n@pa@jKhMnoAoA`\\bd@h]n]zxAxd@xwAf[dW`Nn}@n{@`eAh^xgBlm@dn@nIpdBfg@vX~p@bpAt[zr@o[piAcVhdA~@ja@xXhTh@r|@}@pcBfa@~_Arn@~v@wt@jrAsUxbC|@`uBzN~lB{YzmAy\\znBwn@vqA~KpaBbLv\\mOxs@nUxkB`Wxx@cAr~AaZpvBzRdtBr~@rzAbqAvpNoBxrDjmAxzDnJj{Dn]|nChFjtCvVfmFvF`_Fp{BhkLo@hyB``AjdBxbArrCvQ`{Ev{@rpCj_C`dC~nCheDpaA`aA`xAnfDdf@vv@pfA`zC|z@tnA|~AtO|[haA|k@dx@`}@fW|m@j_Ab~C`vAbaBh}@xXdyAp}Al|@tc@`^zm@uIvmAqDdA|gA~X|WzR_Hnb@evAjuAyB`ThQjbA~w@lHr~@fRvRhg@}F`q@b\\f`AhqAp{AtYnl@vmAx|@je@lr@zPr\\aEtZl]eEzdAtJ|vBqQdjBn_@jqCfz@peHrj@xM|r@nf@|m@rmBxSbpAta@luCp|@z_G",
    "weather_data": [
      ...
      {
        "alerts": "EMPTY",
        "latitude": 39.66086,
        "longitude": -105.9867,
        "timezone": "America/Denver",
        "weather_data": {
          "apparentTemperature": 39.4,
          "cloudCover": 0,
          "dewPoint": 10.51,
          "humidity": 0.27,
          "icon": "clear-day",
          "ozone": 337.6,
          "precipIntensity": 0,
          "precipProbability": 0,
          "pressure": 1011.5,
          "summary": "Clear",
          "temperature": 42.23,
          "time": 1590076800,
          "uvIndex": 6,
          "visibility": 2.612,
          "windBearing": 173,
          "windGust": 8.27,
          "windSpeed": 4.59
        }
      },
      {
        "alerts": [
          {
            "description": "...FIRE WEATHER WATCH IN EFFECT FROM FRIDAY AFTERNOON THROUGH FRIDAY EVENING FOR GUSTY WINDS, LOW RELATIVE HUMIDITY AND DRY FUELS FOR COLORADO FIRE WEATHER ZONES 290, 292 AND 203, ZONES 205, AND 207 BELOW 8000 FEET AND ZONE 294 BELOW 9500 FEET AND UTAH FIRE WEATHER ZONE 490... ...FIRE WEATHER WATCH IN EFFECT FROM FRIDAY AFTERNOON THROUGH FRIDAY EVENING FOR GUSTY WINDS, LOW RELATIVE HUMIDITY AND DRY FUELS FOR FIRE WEATHER ZONES 203, 205, AND 207 BELOW 8000 FEET... The National Weather Service in Grand Junction has issued a Fire Weather Watch below 8000 feet for gusty winds, low relative humidity and dry fuels, which is in effect from Friday afternoon through Friday evening. * AFFECTED AREA...In Colorado, Fire Weather Zone 203 Lower Colorado River, Fire Weather Zone 205 Colorado River Headwaters and Fire Weather Zone 207 Southwest Colorado Lower Forecast Area below 8000 feet. * WINDS...Southwest 15 to 25 mph with gusts up to 35 mph. * RELATIVE HUMIDITY...7 to 12 percent. * IMPACTS...Conditions may become favorable for the rapid ignition, growth and spread of fires.\n",
            "expires": 1590202800,
            "regions": [
              "Colorado River Headwaters",
              "Lower Colorado River",
              "Southwest Colorado Lower Forecast Area"
            ],
            "severity": "watch",
            "time": 1590170400,
            "title": "Fire Weather Watch",
            "uri": "https://alerts.weather.gov/cap/wwacapget.php?x=CO125F4CE21FE0.FireWeatherWatch.125F4CFFDDF0CO.GJTRFWGJT.c302b69e340a3131a59a940c9118e142"
          },
          {
            "description": "...Rivers and Streams Will Continue to Run High this Week into the Weekend due to Snowmelt... Flows in area rivers, streams, and creeks will continue to run at elevated levels as the recent snowmelt works downstream. Significant flooding is NOT forecast at this time as many waterways peak over the next week. Many smaller streams and creeks will run at bankfull conditions through the end of the week causing localized lowland flooding. Anyone planning to recreate on area waterways should maintain awareness and use an abundance of caution in or near the water. Areas that will need to be watched closely include: The Yampa River, Elk River, upper Slater Fork, and other small streams in the upper Yampa, White, and Eagle Basins.\n",
            "expires": 1590451200,
            "regions": [
              "Eagle",
              "Garfield",
              "Moffat",
              "Rio Blanco",
              "Routt"
            ],
            "severity": "advisory",
            "time": 1589913240,
            "title": "Hydrologic Outlook",
            "uri": "https://alerts.weather.gov/cap/wwacapget.php?x=CO125F4CC52C28.HydrologicOutlook.125F4D2D2F80CO.GJTESFGJT.cf955ef1e2c1028fe1acbe4ea736bb0b"
          }
        ],
        "latitude": 39.6728,
        "longitude": -106.79992,
        "timezone": "America/Denver",
        "weather_data": {
          "apparentTemperature": 54.84,
          "cloudCover": 0,
          "dewPoint": 20.74,
          "humidity": 0.26,
          "icon": "clear-day",
          "ozone": 342.2,
          "precipIntensity": 0,
          "precipProbability": 0,
          "pressure": 1012.4,
          "summary": "Clear",
          "temperature": 54.84,
          "time": 1590080400,
          "uvIndex": 7,
          "visibility": 10,
          "windBearing": 238,
          "windGust": 15.94,
          "windSpeed": 9.35
        }
      },
      ...
    ]
  },
  "end_addr": "Grand+Junction,+CO",
  "start_addr": "Denver,+CO",
  "status": "OK"
}
```
## Tasks
- [x] configure app to run on gunicorn
- [ ] optimize gunicorn settings for prod
- [ ] fix logging since gunicorn doesn't use logging class
- [ ] set up SSL
- [ ] set up mutual authentication
- [ ] create config file to store API keys
- [ ] create config files for webapp settings (request timeout, port, etc...)
