# Delta Wi-Fi Positioning System
An indoor positioning system using lateration and geometric methods for use in the University of Tartu Delta Centre.


## Project Structure

....


### Installing

```
$ git clone https://github.com/tonysln/delta-wifi-pos.git
$ cd delta-wifi-pos
$ pip install -r requirements.txt
```


### Running
If you're using Windows as your operating system:

```
$ python3 app.py
```

In case of macOS you will need sudo privileges:
```
$ sudo python3 app.py
```

In case of Linux you will also need to specify the name of your Wi-Fi adapter:
```
$ sudo python3 app.py --adapter NAME
```

On some Linux builds, the following error might be displayed, due to a bug in PySide 6:

```
ImportError: libOpenGL.so.0: cannot open shared object file: No such file or directory
```

You might need to install the `libopengl0` library to fix this.


### Configuration

All constant variables used throughout the app are saved in `config.ini` and can be changed to possibly improve the accuracy. 

Some useful variables to configure:

- `DIST_THRESHOLD` - expressed in pixels. All nearby routers above this value are ignored.
- `RAD_THRESHOLD` - expressed in meters. Precision will be clamped by this value (max).
- `PX_SCALE` - the amount of pixels to cover one meter of real distance.
- `RSSI_MIN` - expressed in dBm. All nearby routers below this value are excluded.
- `PATH_LOSS` exponent. Influences the conversion algorithm between RSSI and distance.
- `POWER` value. Influences the conversion between RSSI and distance.
- `AUTO_SEC` - expressed in seconds. Number of seconds between auto-scan activations.