import logging

from aiohttp import ClientSession, TCPConnector

from models.derpibooru import Image, SearchPayload


class DerpibooruFilters:
    EVERYTHING = 56027
    DEFAULT = 100073


class DerpibooruClient:
    base_url = 'https://derpibooru.org/api/v1/json'

    def __init__(self, filter_id=DerpibooruFilters.DEFAULT, max_connections=5):
        self.filter_id = filter_id
        self.session = ClientSession(connector=TCPConnector(limit=max_connections))

    async def search_images(self, query: str, sf='created_at', sd='desc', per_page=50, page=1, filter_id=None):
        params = {
            'q': query, 'sf': sf, 'sd': sd, 'filter_id': filter_id or self.filter_id,
            'per_page': per_page, 'page': page}
        async with self.session.get(f'{self.base_url}/search/images', params=params, raise_for_status=True) as resp:
            payload = await resp.json(encoding='utf-8')
            return SearchPayload.from_dict(payload)

    async def iter_search(self, query: str, start_page=1, **search_kwargs):
        current_page, fetched, total = start_page, 0, 1.1
        while fetched < total:
            response = await self.search_images(query, page=current_page, **search_kwargs)
            if total != 1.1 and total != response.total:
                logging.getLogger(__name__).warning(
                    f'Number of images matching the query during iterations changed '
                    f'from {total} to {response.total}. {query=!r}')
            total = response.total
            if total == 1.1:
                total = response.total
            yield response
            current_page += 1
            fetched += len(response.images)

    async def featured_image(self):
        async with self.session.get(f'{self.base_url}/images/featured', raise_for_status=True) as resp:
            payload = await resp.json(encoding='utf-8')
            return Image.from_dict(payload['image'])
