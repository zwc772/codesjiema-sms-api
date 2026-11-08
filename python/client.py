"""Minimal CodesJiema API client. Docs: https://codesjiema.com/apidoc"""
import os
import time
import uuid

import requests

BASE_URL = "https://codesjiema.com"


class CodesJiemaError(Exception):
    pass


class Client:
    def __init__(self, api_key=None, base_url=BASE_URL, timeout=45):
        self.api_key = api_key or os.environ.get("CODESJIEMA_API_KEY")
        if not self.api_key:
            raise CodesJiemaError("Set CODESJIEMA_API_KEY or pass api_key=")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["X-API-Key"] = self.api_key

    def _call(self, method, path, params=None, data=None):
        for attempt in range(3):
            r = self.session.request(method, self.base_url + path, params=params, data=data, timeout=self.timeout)
            if r.status_code == 429:  # rate limited
                time.sleep(int(r.headers.get("Retry-After", 5)))
                continue
            if r.status_code in (401, 403):
                raise CodesJiemaError(f"HTTP {r.status_code}: check your API key / access")
            body = r.json()
            if body.get("code") != 1:
                raise CodesJiemaError(body.get("msg") or "request failed")
            return body.get("data") or {}
        raise CodesJiemaError("too many requests, try later")

    def get(self, path, **params):
        return self._call("GET", path, params=params)

    def post(self, path, **data):
        return self._call("POST", path, data=data)

    @staticmethod
    def new_idempotency_key():
        # 16-64 chars; reuse the SAME key when retrying a timed-out paid request
        return uuid.uuid4().hex
