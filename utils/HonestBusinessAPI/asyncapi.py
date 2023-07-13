from typing import Dict

from utils.HonestBusinessAPI.base import BaseAsyncClient


class HonesBusinessClient(BaseAsyncClient):
    async def data_search(self, string: str) -> Dict:
        """Поиск (search)"""
        return await self._request("get", "/paid/data/search?api_key={token}&string={params}", string)

    async def card(self, id_: str) -> Dict:
        """Основные сведения (card)"""
        return await self._request("get", "/paid/data/card?api_key={token}&id={params}", id_)

    async def fl_card(self, id_: str) -> Dict:
        """Сведения о Физ. лице (fl-card)"""
        return await self._request("get", "/paid/data/fl-card?api_key={token}&id={params}", id_)

    async def fns_card(self, id_: str) -> Dict:
        """Сведения ФНС (fns-card)"""
        return await self._request("get", "/paid/data/fns-card?api_key={token}&id={params}", id_)

    async def diffs(self, id_: str) -> Dict:
        """Изменения (diffs)"""
        return await self._request("get", "/paid/data/diffs?api_key={token}&id={params}", id_)

    async def requisites(self, id_: str) -> Dict:
        """Реквизиты (requisites)"""
        return await self._request("get", "/paid/data/requisites?api_key={token}&id={params}", id_)

    async def affilation_company(self, id_: str) -> Dict:
        """Связанные организации"""
        return await self._request("get", "/paid/data/affilation-company?api_key={token}&id={params}", id_)

    async def court_arbitration(self, id_: str) -> Dict:
        """Судебные дела (court-arbitration)"""
        return await self._request("get", "/paid/data/court-arbitration?api_key={token}&id={params}", id_)

    async def zakupki_top(self, id_: str) -> Dict:
        """ТОП закупок (zakupki-top)"""
        return await self._request("get", "/paid/data/zakupki-top?api_key={token}&id={params}", id_)

    async def fssp_list(self, id_: str) -> Dict:
        """ФССП (fssp-list)"""
        return await self._request("get", "/paid/data/fssp-list?api_key={token}&id={params}", id_)

    async def proverki(self, id_: str) -> Dict:
        """Проверки (proverki)"""
        return await self._request("get", "/paid/data/proverki?api_key={token}&id={params}", id_)

    async def licenses(self, id_: str) -> Dict:
        """Лицензии"""
        return await self._request("get", "/paid/data/licenses?api_key={token}&id={params}", id_)

    async def important_facts(self, id_: str) -> Dict:
        """Лицензии"""
        return await self._request("get", "/paid/data/important-facts?api_key={token}&id={params}", id_)


