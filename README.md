# Delta Wi-Fi Positioning System
An indoor positioning system using lateration and geometric methods for use in the University of Tartu Delta Centre.


### Project Structure
```shell
/
├── data
│     └── routers.csv             # Main routers database
├── map
│     ├── korrus-1-c.png          # Cleaned up and original versions
│     ├── korrus-1.png            # of maps for every floor in Delta
│     ├── korrus-1-overlay.png    # Overlays for floor maps
│     └── ...
├── ui                      
│     ├── app_main.ui             # Main app window UI file for PySide
│     └── components.py           # Classes for various UI components
├── app.py                        # Main app script file
├── config.json                   # Configuration file
├── install.sh                    # Easy install and setup bash script
├── locator.py                    # All methods required for positioning
├── requirements.txt              # List of Python packages to install
├── scanner.py                    # Methods for envoking and parsing network scans
└── start.sh                      # Start bash script
```


### Installing

```
$ git clone https://github.com/tonysln/delta-wifi-pos.git
$ cd delta-wifi-pos
$ pip install -r requirements.txt
```

Alternatively, the `install.sh` script file can be downloaded and launched to complete the installation automatically.


### Running
If you're using Windows as your operating system:

```
$ python3 app.py
```

In case of macOS and Linux you will need sudo privileges:
```
$ sudo python3 app.py
```

In case of Linux you will also need to specify the name of your Wi-Fi adapter inside the `config.json` file, on line 2:
```
"ADAPTER": "add_name_here",
```

On some Linux builds, the following error might be displayed, due to a bug in PySide 6:

```
ImportError: libOpenGL.so.0: cannot open shared object file: No such file or directory
```

You might need to install the `libopengl0` library to fix this.


### Configuration

All constant variables used throughout the app are saved in `config.json` and can be changed to possibly improve the accuracy. 

Some useful variables to configure:

- `DIST_THRESHOLD` - expressed in pixels. All nearby routers above this value are ignored.
- `RAD_THRESHOLD` - expressed in meters. Precision will be clamped by this value (max).
- `PX_SCALE` - the amount of pixels to cover one meter of real distance.
- `RSSI_MIN` - expressed in dBm. All nearby routers below this value are excluded.
- `PATH_LOSS` exponent. Influences the conversion algorithm between RSSI and distance.
- `POWER` value. Influences the conversion between RSSI and distance.
- `AUTO_SEC` - expressed in seconds. Number of seconds between auto-scan activations.
- `MIN_FLOOR` and `MAX_FLOOR` - the lowest and highest floor numbers used in the application.
