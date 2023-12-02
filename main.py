import asyncio
import logging
import sys

from clients.derpibooru import DerpibooruClient
from features.sync_by_query import sync_images_by_query


async def main():
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('output.log')]
    )
    client = DerpibooruClient()
    await sync_images_by_query(client, 'oc:hardy')
    await client.session.close()


if __name__ == '__main__':
    asyncio.run(main())
