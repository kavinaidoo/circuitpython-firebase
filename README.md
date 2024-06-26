# circuitpython-firebase

Fork of [micropython-firebase-auth](https://github.com/WoolDoughnut310/micropython-firebase-auth) and [micropython-firebase-firestore](https://github.com/WoolDoughnut310/micropython-firebase-firestore) by [WoolDoughnut310](https://github.com/WoolDoughnut310) which are based on [micropython-firebase-realtime-database](https://github.com/ckoever/micropython-firebase-realtime-database) by [ckoever](https://github.com/ckoever)


## Firebase Auth

Available functions:
```
- sign_in
- sign_out
- sign_up
```
Install by copying firebase_auth.mpy to the /lib/ folder on your microcontroller.

See WoolDoughnut310's readme [here](https://github.com/WoolDoughnut310/micropython-firebase-auth/blob/master/README.md) for example usage.

## Firestore

Available functions*:
```
- patch
- create
- get
```
Install by copying ufirestore.mpy to the /lib/ folder on your microcontroller.

See WoolDoughnut310's readme [here](https://github.com/WoolDoughnut310/micropython-firebase-firestore/blob/master/README.md) for example usage.

Note: This fork removes callbacks and background execution so omit _bg_ and _cb_ parameters when calling functions.

## Requirements

- Adafruit CircuitPython v9.x
- [adafruit_requests](https://github.com/adafruit/Adafruit_CircuitPython_Requests) which itself requires [adafruit-circuitpython-connectionmanager](https://github.com/adafruit/Adafruit_CircuitPython_ConnectionManager)
    - Click the above links, go to Releases, download the latest 9.x mpy versions and install by unzipping and copying the contents of the /lib/ folders to the /lib/ folder on your microcontroller.

## Example Code

See [example.py](https://github.com/kavinaidoo/circuitpython-firebase/blob/main/example.py).

## Notes

*[micropython-firebase-firestore](https://github.com/WoolDoughnut310/micropython-firebase-firestore) has more functions that you may want to use. You can add these functions by porting in and modifying the relevant code from that repo.

Non-compiled versions are available: firebase_auth.py and ufirestore.py

Code was developed/tested/compiled using the following:
- adafruit-circuitpython-requests-9.x-mpy-3.2.3
- adafruit-circuitpython-connectionmanager-9.x-mpy-1.0.1
- Adafruit CircuitPython 9.0.5 on Raspberry Pi Pico W
- mpy-cross-macos-11-9.0.5-universal