#!/usr/bin/env python
"""
Command line tool to process the backup files provided by Flickr.
"""
import argparse
import logging

from flickr.handlers import FlickrAlbumsHandler


logger = logging.getLogger("flickr_backup")


def setup_argparse() -> argparse.ArgumentParser:
    """
    Setups the argparse tool.
    """
    parser = argparse.ArgumentParser(description="Flickr backup files utility.")
    parser.add_argument("photos_dir", action="store", help="Folder where photos are located.")
    parser.add_argument(
        "-o", "--output_dir", action="store", help="Output folder. Defaults to 'photos_dir'."
    )
    parser.add_argument(
        "-a",
        "--album_json",
        action="store",
        help="Folder where the 'albums.json' is located. Defaults to 'photos_dir'.",
    )
    parser.add_argument(
        "-v", "--verbosity", action="store_true", help="Adds verbosity.",
    )

    return parser


if __name__ == "__main__":
    # Arguments parsing
    parser = setup_argparse()
    args = parser.parse_args()

    if not args.verbosity:
        logger.setLevel(logging.INFO)

    if args.album_json:
        flickr_albums = FlickrAlbumsHandler(
            args.album_json, args.photos_dir, output_dir=args.output_dir
        )
    else:
        flickr_albums = FlickrAlbumsHandler(
            args.photos_dir, args.photos_dir, output_dir=args.output_dir
        )

    flickr_albums.make()
