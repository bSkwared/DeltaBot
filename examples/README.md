# API Sample Code

The [get-guild-allycodes.py](get-guild-allycodes.py) file will collect a list of
guild member allycodes. Update the script with an API username, password and the allycode of
a guild member before executing.

The [swgoh-sample.py](swgoh-example.py) file is a collection of example code to illustrate
usage of various API endpoints. It is not intended to be run as is. 


Update lines 4 and 5 in [get-guild-allycodes.py](get-guild-allycodes.py) before executing.
```
# Change the settings below
allycode = 123456789
creds = settings('<USERNAME>', '<PASSWORD>')
```

## Usage

**Note: output has been truncated and masked for display purposes**
```buildoutcfg
/usr/local/bin/python3.9 get-guild-allycodes.py
[8544XXXXX, 6355XXXXX, 1971XXXXX, 1843XXXXX, ...]
```