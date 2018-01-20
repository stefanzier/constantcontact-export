'''
Jordan Clark
2015 - Blitzen.com
'''

import requests
import re
import json

BASE_URL = 'https://api.constantcontact.com/v2/'


class ConstantContactError(Exception):

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return self.response.get('error', 'No error provided')


class IncorrectApiKey(ConstantContactError):
    pass


class ConstantContact(object):

    def __init__(self, api_key, access_token):
        self.api_key = api_key
        self.access_token = access_token
        self._attr_path = []
        self._request_method = {
            'POST': requests.post,
            'GET': requests.get,
            'PUT': requests.put,
            'DELETE': requests.delete,
            }

    def __call__(self, *args, **kwargs):
        url = BASE_URL + '/'.join(self._attr_path)
        added_limit = False
        for variable_name, variable_sub in kwargs.get('variable', {}).items():
            url = re.sub(variable_name, variable_sub, url)
            if "limit" in kwargs.get('variable') and not added_limit:
                url += "?limit=500"
                added_limit = True

        self._attr_path = []
        return self._request(
                url,
                kwargs.get('data', {}),
                kwargs.get('method', 'GET'),
                kwargs.get('params', {})
            )

    def __getattr__(self, attr, *args, **kwargs):
        self._attr_path.append(attr)
        return self

    def _request(self, endpoint, data, method='GET', params={}):
        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        params['api_key'] = self.api_key

        if(type(data) == dict):
            data = json.dumps(data)

        try:
            request = self._request_method[method]
        except KeyError:
            raise ConstantContactError('Unknown verb')

        response = request(
            endpoint,
            data=data,
            params=params,
            headers=headers
        )

        if response.status_code < 400:
            return response.json()
        else:
            response.raise_for_status()
