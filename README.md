# ObjectBoxLite

In my bachelor thesis I developed a forensic tool **ObjectBoxLite** to give the community the possibility to analyze ObjectBox Database files :coffee: :man_technologist:. [ObjectBox](https://objectbox.io/) is a non SQLite Database, that is developed for Mobile-, Edge- or IoT-Computing. The Database file can extracted from Smartphone Apps or from IoT devices. 

## Background

The tool are based on [Kaitai Struct](https://kaitai.io/) to parse the database file. A formal description of the binary structure of an ObjectBox database file is saved in /ks/mdb.ksy. That description was compile to the python module /ks/mdb.py and imported to the tool. 

The tool is able to read actually tables and entries from the database file.

## System
Tool runs and tested under Mac OS X and Python 3.9.6.