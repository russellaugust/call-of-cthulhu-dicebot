#!/usr/bin/env python3

import yaml

SETTINGSFILE = "settings.yaml"

class Settings:

    def __init__(self):
        self.__settings__ = {}
        with open(SETTINGSFILE) as f:
            self.__settings__ = yaml.load(f, Loader=yaml.FullLoader)

    def __update__(self, field, info):
        with open(SETTINGSFILE, 'w') as outfile:
            self.__settings__[field] = info
            yaml.dump(self.__settings__, outfile, default_flow_style=False)
            
        
    @property
    def announce(self):
        return self.__settings__['announce']

    @announce.setter
    def announce(self, announce_bool):
        if isinstance(announce_bool, bool):
            self.__update__("announce", announce_bool)
        else:
            raise ValueError('This needs to be True or False')

    @property
    def card_path(self):
        return self.__settings__['card_path']

    @card_path.setter
    def card_path(self, input):
        self.__update__("card_path", input)


    @property
    def database_path(self):
        return self.__settings__['database_path']

    @database_path.setter
    def database_path(self, input):
        self.__update__("database_path", input)


    @property
    def audio_rolls_path(self):
        return self.__settings__['audio_rolls_path']
