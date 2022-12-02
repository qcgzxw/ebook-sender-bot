import json
import typing

import requests
import urllib3


class MailcowException(Exception):
    pass


class MailcowServerException(Exception):
    pass


REQUEST_CONFIG_CONTENT_TYPE = "application/json"
REQUEST_CONFIG_SSL_VERIFY = False


class MailcowHelper:
    def __init__(self, api_url, api_key):
        self._api_url = api_url
        self._api_key = api_key
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def add(self, source: str, data: object) -> (bool, object):
        http_code, data = self._post(self._build_url(f"api/v1/add/{source}"), json.dumps(data))
        return http_code, data

    def delete(self, source: str, data: object) -> (bool, object):
        http_code, data = self._post(self._build_url(f"api/v1/delete/{source}"), json.dumps(data))
        return http_code, data

    def update(self, source: str, data: object) -> (bool, object):
        http_code, data = self._post(self._build_url(f"api/v1/update/{source}"), json.dumps(data))
        return http_code, data

    def get(self, source, source_id: str) -> object:
        http_code, data = self._get(self._build_url(f"api/v1/get/{source}/{source_id}"))
        if http_code != 200:
            raise MailcowException(data)
        return data

    def _build_url(self, url: str) -> str:
        return f"{self._api_url}/{url}"

    def _post(self, api_url, json_data: str) -> (bool, object):
        headers = {'X-API-Key': self._api_key, 'Content-type': REQUEST_CONFIG_CONTENT_TYPE}
        req = requests.post(api_url, headers=headers, data=json_data, verify=REQUEST_CONFIG_SSL_VERIFY)
        try:
            rsp = req.json()
        except Exception as e:
            raise MailcowServerException(e)
        req.close()

        if "type" in rsp[0] and "msg" in rsp[0]:
            if rsp[0]['type'] != 'success':
                return False, rsp[0]['msg']
            else:
                return True, None
        else:
            return False, f"Got malformed response! Is {self._api_url} a mailcow server?"

    def _get(self, request_url: str) -> (int, object):
        headers = {'X-API-Key': self._api_key, 'Content-type': REQUEST_CONFIG_CONTENT_TYPE}
        req = requests.get(request_url, headers=headers, verify=REQUEST_CONFIG_SSL_VERIFY)
        try:
            rsp = req.json()
        except Exception as e:
            raise MailcowServerException(e)
        req.close()

        if req.status_code != 200:
            if "type" in rsp and "msg" in rsp:
                return req.status_code, rsp["msg"]
            else:
                return req.status_code, f"Got malformed response! Is {self._api_url} a mailcow server?"

        return req.status_code, rsp
