# evekit.reference.Client module
"""
Convenience objects for creating various swagger clients:

* SDE        - Client for the EVE Static Data Export service hosted by Orbital Enterprises
* MarketData - Client for Market Data service hosted by Orbital Enterprises
* ESI        - Client for CCP's EVE Swagger Interface
* ESIProxy   - Client for the EVE Swagger Interface Proxy hosted by Orbital Enterprises
* Citadel    - Client for the Structure Name API at https://stop.hammerti.me.uk/api/

"""
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from bravado.requests_client import Authenticator


class __ExternalClientMap:
    """
    Internal class which maintains a cache of external clients
    """
    def __init__(self):
        self.client_map = {}

    def get(self, client_type, key):
        if client_type not in self.client_map:
            return None
        return self.client_map[client_type][key]

    def set(self, client_type, key, value):
        if client_type not in self.client_map:
            self.client_map[client_type] = {}
        self.client_map[client_type][key] = value


def __mk_key__(*args):
    """
    Create a key by concatenating strings
    :param args: string arguments to concatenate
    :return: concatenated key
    """
    return "_".join(args)

__external_clients__ = __ExternalClientMap()
"""
Internal module variable maintaining client map.
"""


class SDE:
    @staticmethod
    def get(version=None):
        """
        Get a Swagger client for the Orbital Enterprises SDE service
        :param version: version of SDE to retrieve, defaults to 'latest'
        :return: a SwaggerClient for the requested SDE
        """
        global __external_clients__
        if version is None:
            version = 'latest'
        sde_url = "https://evekit-sde.orbital.enterprises/latest/swagger.json"
        if version != 'latest':
            sde_url = "https://evekit-sde.orbital.enterprises/%s/api/ws/v%s/swagger.json" % (version, version)
        existing = __external_clients__.get('SDE', version)
        if existing is None:
            existing = SwaggerClient.from_url(sde_url,
                                              config={'use_models': False,
                                                      'validate_responses': False,
                                                      'also_return_response': True})
            __external_clients__.set('SDE', version, existing)
        return existing

    @staticmethod
    def load_complete(query_func, **kwargs):
        result = []
        kwargs['contid'] = 0
        batch, status = query_func(**kwargs).result()
        while status.status_code == 200 and len(batch) > 0:
            result.extend(batch)
            kwargs['contid'] += len(batch)
            batch, status = query_func(**kwargs).result()
        return result


class MarketData:
    @staticmethod
    def get():
        """
        Get a Swagger client for the Orbital Enterprises Market Data service
        :return: a SwaggerClient for the Market Data service
        """
        global __external_clients__
        existing = __external_clients__.get('MarketData', True)
        if existing is None:
            existing = SwaggerClient.from_url("https://evekit-market.orbital.enterprises//swagger",
                                              config={'use_models': False,
                                                      'validate_responses': False,
                                                      'also_return_response': True})
            __external_clients__.set('MarketData', True, existing)
        return existing


class ESI:
    @staticmethod
    def get(release='latest', source='tranquility'):
        """
        Get a Swagger client for the EVE Swagger Interface
        :param release: ESI release.  One of 'latest', 'legacy' or 'dev'.
        :param source: ESI source.  One of 'tranquility' or 'singularity'.
        :return: a SwaggerClient for the EVE Swagger Interface
        """
        global __external_clients__
        existing = __external_clients__.get('ESI', __mk_key__(release, source))
        if existing is None:
            url = "https://esi.tech.ccp.is/%s/swagger.json?datasource=%s" % (release, source)
            existing = SwaggerClient.from_url(url,
                                              config={'use_models': False,
                                                      'validate_responses': False,
                                                      'also_return_response': True})
            __external_clients__.set('ESI', __mk_key__(release, source), existing)
        return existing


class Citadel:
    @staticmethod
    def get():
        """
        Get a Swagger client for the Structure Name API at https://stop.hammerti.me.uk/api/
        :return: a SwaggerClient for the Structure Name API
        """
        global __external_clients__
        existing = __external_clients__.get('Citadel', True)
        if existing is None:
            url = "https://raw.githubusercontent.com/OrbitalEnterprises/swagger-specs/master/citadel-api.yaml"
            existing = SwaggerClient.from_url(url,
                                              config={'use_models': False,
                                                      'validate_responses': False,
                                                      'also_return_response': True})
            __external_clients__.set('Citadel', True, existing)
        return existing


class ApiKeyPairAuthenticator(Authenticator):
    """
    Bravado authenticator which accepts two query based API keys
    """
    def __init__(self, host, key_1_name, key_1_key, key_2_name, key_2_key):
        super(ApiKeyPairAuthenticator, self).__init__(host)
        self.key_1_name = key_1_name
        self.key_1_key = key_1_key
        self.key_2_name = key_2_name
        self.key_2_key = key_2_key

    def apply(self, request):
        request.params[self.key_1_name] = self.key_1_key
        request.params[self.key_2_name] = self.key_2_key
        return request


class AuthRequestsClient(RequestsClient):
    """
    Customized Bravado RequestClient which allows setting an authenticator directly
    """
    def set_auth(self, auth):
        self.authenticator = auth


class ESIProxy:
    @staticmethod
    def get(api_key, api_hash, release='latest', source='tranquility'):
        """
        Get a Swagger client for the Proxied EVE Swagger Interface
        :param api_key: Proxy api key.
        :param api_hash: Proxy api hash.
        :param release: ESI release.  One of 'latest', 'legacy' or 'dev'.
        :param source: ESI source.  One of 'tranquility' or 'singularity'.
        :return: a SwaggerClient for the EVE Swagger Interface
        """
        global __external_clients__
        key = __mk_key__(api_key, api_hash, release, source)
        existing = __external_clients__.get('ESIProxy', key)
        if existing is None:
            pair_auth = ApiKeyPairAuthenticator('esi-proxy.orbital.enterprises',
                                                'esiProxyKey', api_key,
                                                'esiProxyHash', api_hash)
            http_client = AuthRequestsClient()
            http_client.set_auth(pair_auth)
            url = "https://esi-proxy.orbital.enterprises/%s/swagger.json?datasource=%s" % (release, source)
            existing = SwaggerClient.from_url(url,
                                              http_client=http_client,
                                              config={'use_models': False,
                                                      'validate_responses': False,
                                                      'also_return_response': True})
            __external_clients__.set('ESIProxy', key, existing)
        return existing
