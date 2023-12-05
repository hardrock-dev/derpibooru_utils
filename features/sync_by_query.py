import asyncio
import logging
import re
from pathlib import Path

from tqdm import tqdm

from clients.derpibooru import DerpibooruClient
from models.derpibooru import Image

log = logging.getLogger(__name__)


def gen_image_path(save_dir: Path, image: Image):
    return (save_dir / str(image.id)).with_suffix(f'.{image.format}')


async def download_image(
        save_dir: Path, image: Image, client: DerpibooruClient, representation='full', pbar: tqdm = None):
    file = gen_image_path(save_dir, image)
    if file.exists():
        log.debug(f'Saved image for {image.id} already exists')
        if pbar:
            pbar.update(1)
        return

    try:
        async with client.session.get(image.representations[representation], raise_for_status=True) as resp:
            file.write_bytes(await resp.read())
            log.debug(f'Saved image for {image.id} -> {file.absolute().as_uri()}')
    finally:
        if pbar:
            pbar.update(1)


async def save_image_tags(save_dir: Path, image: Image, recheck_saved=True):
    file = gen_image_path(save_dir, image).with_suffix(f'.txt')
    if file.exists() and not recheck_saved:
        log.debug(f'Saved tags for {image.id} already exists')
        return

    tags = ','.join(image.tags)
    if not (file.exists() and (file.read_text() == tags)):
        file.write_text(tags, encoding='utf-8')
        log.debug(f'Saved tags for {image.id} -> {file.absolute().as_uri()}')


async def sync_images_by_query(
        client: DerpibooruClient, query: str, *, base_save_dir=None, incremental=True, save_tags=True, fetch_limit=300,
        start_page=1):
    dir_name = re.sub(r'[^\w= ]+', '', query.replace(':', '='))
    save_dir = Path(base_save_dir or 'downloads/sync') / dir_name
    save_dir.mkdir(parents=True, exist_ok=True)

    log.info(f'Preparing to sync {query!r} in dir {save_dir.absolute().as_uri()}')

    query_file = save_dir / 'query.txt'
    if query_file.exists():
        assert query_file.read_text() == query, 'Queries are expected to be equal'
    else:
        query_file.write_text(query)

    images_dir = save_dir / 'images'
    images_dir.mkdir(exist_ok=True)

    images = []
    page = start_page
    async for resp in client.iter_search(query, start_page):
        images.extend(resp.images)
        log.debug(f'Fetched {len(images)} images to sync')
        if incremental and gen_image_path(images_dir, images[-1]).exists():
            break
        if fetch_limit is not None and len(images) >= fetch_limit:
            log.warning(
                f'{fetch_limit=} reached at {page=}. Total search results={resp.total}. '
                f'If you want to download more than {fetch_limit} images you can:\n'
                f'- Increase fetch_limit\n- Use start_page={page} arg and continue downloading\n'
                f'- Disable fetch limit via fetch_limit=None (it may be dangerous)')
            images = images[:fetch_limit]
            break
        page += 1

    log.info(f"Found {len(images)} to{' incremental' if incremental else ''} sync")

    if save_tags:
        tags_dir = save_dir / 'tags'
        tags_dir.mkdir(exist_ok=True)
        results = await asyncio.gather(
            *(save_image_tags(tags_dir, img, recheck_saved=False) for img in images), return_exceptions=True)
        for res in results:
            if isinstance(res, Exception):
                log.exception('Exception in save_image_tags', exc_info=res)

    with tqdm(total=len(images), desc='Downloading images') as pbar:
        results = await asyncio.gather(
            *(download_image(images_dir, img, client, pbar=pbar) for img in images), return_exceptions=True)

        for img, res in zip(images, results):
            if isinstance(res, Exception):
                log.exception(f'Cannot download {img.id}', exc_info=res)

    log.info('Done!')
    return images
