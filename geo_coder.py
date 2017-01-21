from geopy.geocoders import Yandex


class ParametrisibleYandexGeoCoder(Yandex):
    def geocode(self, query, extra_params=None, exactly_one=True, timeout=None):
        params = {
            'geocode': query,
            'format': 'json'
        }
        extra_params = extra_params or {}
        params.update(extra_params)
        if not self.api_key is None:
            params['key'] = self.api_key
        if not self.lang is None:
            params['lang'] = self.lang
        if exactly_one is True:
            params['results'] = 1
        url = "?".join((self.api, urlencode(params)))
        logger.debug("%s.geocode: %s", self.__class__.__name__, url)
        return self._parse_json(
            self._call_geocoder(url, timeout=timeout),
            exactly_one,
        )
