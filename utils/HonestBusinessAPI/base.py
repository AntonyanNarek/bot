from typing import Dict, TypeVar, Optional

import httpx

from config_data.config import load_config

T = TypeVar("T", bound="BaseClient")


class BaseClient:
    def __init__(self, token: Optional[str] = None, timeout: Optional[float] = 10):
        if token is None:
            config = load_config()
            token = config.api_config.zcb_token
        assert (token is not None), "Token not found. Use Client(token='<token>') or set env TOKEN=<token>"

        self._url = 'https://zachestnyibiznesapi.ru{}'
        self._token = token
        self._path = 'PARAMETERS&api_key={}'
        self._timeout = timeout
        self._headers = {"accept": "application/json"}


class BaseAsyncClient(BaseClient):
    def __init__(self, token: Optional[str] = None, timeout: Optional[float] = 10):
        super().__init__(token=token, timeout=timeout)
        self._client = httpx.AsyncClient()

    async def _request(self, method: str, path: str, params: str) -> Dict:
        url = self._url.format(path).format(token=self._token, params=params)
        resp = await self._client.request(method, url, headers=self._headers, timeout=self._timeout)
        return resp.json()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self: T) -> T:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
