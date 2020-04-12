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
    parser.add_argument("pics_dir", action="store", help="Folder where pics are located.")
    parser.add_argument(
        "-o", "--output_dir", action="store", help="Output folder. Defaults to 'pic_dir'."
    )
    parser.add_argument(
        "-a",
        "--album_json",
        action="store",
        help="Folder where 'albums.json' is located. Defaults to 'pic_dir'.",
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
            args.album_json, args.pics_dir, output_dir=args.output_dir
        )
    else:
        flickr_albums = FlickrAlbumsHandler(
            args.pics_dir, args.pics_dir, output_dir=args.output_dir
        )

    flickr_albums.make()
