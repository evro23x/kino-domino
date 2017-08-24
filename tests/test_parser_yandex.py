# import pytest

from parser_yandex import *


class TestParserYandex:
    # pass
    def test_get_metro_stations_from_hh_api_type(self):
        assert (str(type(get_metro_stations_from_hh_api())) == str("<class 'list'>"))

    def test_get_metro_stations_from_hh_api_not_empty(self):
        assert (len(get_metro_stations_from_hh_api()) > 0)

    def test_add_metro_stations_type(self):
        isinstance(add_metro_stations(get_metro_stations_from_hh_api()), str)
