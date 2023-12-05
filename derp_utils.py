import argparse
import asyncio
import logging
import sys

from clients.derpibooru import DerpibooruClient
from features.sync_by_query import sync_images_by_query

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('output.log')]
)


async def download_images(args):
    client = DerpibooruClient()
    await sync_images_by_query(
        client, args.query,
        base_save_dir=args.dir,
        incremental=not args.check_all,
        save_tags=args.save_tags,
        fetch_limit=args.limit,
        start_page=args.start_page
    )
    await client.session.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('derp_utils', description="Let's do some stuff with Derpibooru API")
    subparsers = parser.add_subparsers()

    download_parser = subparsers.add_parser(
        'download', description='Download images', usage='python -m derp_utils download "oc:hardy" --save-tags')
    download_parser.set_defaults(func=download_images)
    download_parser.add_argument('query', help='Derpibooru search query')
    download_parser.add_argument(
        '--dir', default='downloads/sync', help='The base path for saving images (will be created if it is missing)')
    download_parser.add_argument(
        '-l', '--limit', '--fetch-limit', type=int, default=300, help='Maximum number of images to download')
    download_parser.add_argument(
        '--check-all', action='store_true', help="Don't stop the search after detecting already downloaded images")
    download_parser.add_argument('--save-tags', action='store_true', help='Save image tags to a separate folder')
    download_parser.add_argument('--start-page', type=int, default=1, help='Start downloading with a specific page')

    run_args = parser.parse_args()
    asyncio.run(run_args.func(run_args))
