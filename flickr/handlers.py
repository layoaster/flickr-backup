"""
Set of handlers of the Flickr backup data.
"""
import collections.abc
import json
import logging
import re
import shutil
import os
from os import path
from typing import List, Optional

from flickr.utils import find_duplicates, normalize


logger = logging.getLogger("flickr_backup")


class FlickrAlbums(collections.abc.Mapping):
    """
    Flickr's albums (read-only) collection.
    """

    def __init__(self, raw_albums: dict):
        """
        Class initialization.
        """
        self.albums: dict = dict()
        for album in raw_albums["albums"]:
            self.albums[album["title"]] = {
                "normalized_title": normalize(album["title"], allow_unicode=False),
                "photos": album["photos"],
            }

    def __iter__(self):
        return iter(self.albums)

    def keys(self):
        return self.albums.keys()

    def items(self):
        return self.albums.items()

    def values(self):
        return self.albums.values()

    def __getitem__(self, key) -> dict:
        return self.albums[key]

    def __contains__(self, item) -> bool:
        return item in self.albums

    def __len__(self) -> int:
        return len(self.albums)


class FlickrAlbumsHandler:
    """
    Handlers of the Flickr albums
    """

    #: Flickr's albums JSON filename.
    JSON_FILENAME: str = "albums.json"
    #: Duplicates registry filename.
    DUPLICATES_FILENAME: str = "duplicates.txt"
    #: Directory name for photos without album.
    ALBUMLESS_PICS_DIR: str = "__no_album__"

    def __init__(self, json_dir: str, photos_dir: str, output_dir: Optional[str] = None):
        """
        Class initialization.

        :param json_dir: Absolute or relative path to the `albums.json` file.
        :param photos_dir: Absolute or relative path to the photos directory.
        :param output_dir: Absolute to relative path to the output dir, defaults
            to `photos_dir`.
        """
        with open(path.join(path.abspath(json_dir), self.JSON_FILENAME), "r") as albums_file:
            raw_albums = json.load(albums_file)

        self.albums = FlickrAlbums(raw_albums)
        self.photos_dir = path.abspath(photos_dir)

        if output_dir:
            self.output_dir = path.abspath(output_dir)

            if not path.exists(self.output_dir):
                os.mkdir(self.output_dir)
        else:
            self.output_dir = self.photos_dir

    def _get_pics_filenames(self, pic_ids: List[str]) -> List[str]:
        """
        Find the photo filenames identified by its corresponding Flick photo Id.

        :param pic_id: List of Flickr photo Ids.
        :return: List of photo filenames that are found.
        """
        dir_content = os.listdir(self.photos_dir)
        pattern = re.compile(rf".*_({'|'.join(pic_ids)})_.*")

        return list(filter(pattern.match, dir_content))

    def _create_album(self, name: str, pic_filenames: List[str]):
        """
        Creates an album (directory) and copy its pictures.

        :param name: Album's name.
        :param pic_filenames: List of photo filenames.
        """
        album_dir = path.join(self.output_dir, name)
        if not path.exists(album_dir):
            os.mkdir(album_dir)
        else:
            logger.info(f"Album '{name}' already exists, no photos copied/moved.")
            return

        pics_num = 0
        for filename in pic_filenames:
            full_filename = path.join(self.photos_dir, filename)
            shutil.copy2(full_filename, album_dir)
            logger.debug(f"Photo '{filename}' copied to album '{name}'.")

            pics_num += 1

        logger.info(f"Album '{name}' created with {pics_num} photos.")

    def _duplicates(self, pics_sets: List[set]) -> int:
        """
        Detects photos shared among several albums a write a duplicates registry
        in a text file.

        :param pics_sets: Set of photos per album.
        :return: Number of duplicates.
        """
        duplicates = sorted(find_duplicates(pics_sets))

        with open(path.join(self.output_dir, self.DUPLICATES_FILENAME), "w") as dup_file:
            for filename in duplicates:
                dup_file.write("{}\n".format(filename))

        return len(duplicates)

    def _albumless_pics(self, album_pics: set) -> int:
        """
        Identifies photos that are not included in any album to group them into
        a separate directory.

        :param album_pics: Set of pics that were included in albums.
        :return: Number of photos without album.
        """
        all_pics = set()
        for filename in os.listdir(self.photos_dir):
            if path.isfile(path.join(self.photos_dir, filename)) and not filename.endswith(".json"):
                all_pics.add(filename)

        no_album_pics = all_pics - album_pics

        if no_album_pics:
            self._create_album(self.ALBUMLESS_PICS_DIR, list(no_album_pics))

        return len(no_album_pics)

    def make(self):
        """
        Creates directories with album names and copy/move photos to them.
        """
        pics_sets = []
        for album_metadata in self.albums.values():
            album_pics = self._get_pics_filenames(album_metadata["photos"])
            self._create_album(album_metadata["normalized_title"], album_pics)

            # To find duplicates
            pics_sets.append(set(album_pics))

        # Handling duplicates
        num_duplicates = self._duplicates(pics_sets)

        # Handling photos that has no album.
        album_pics = set.union(*pics_sets)
        num_albumless_pics = self._albumless_pics(album_pics)

        logger.info(
            f"Processed {len(self.albums)} albums and {len(album_pics)} photos of which "
            f"{num_duplicates} are shared among two or more albums."
        )
        logger.info(f"List of shared photos written to {self.DUPLICATES_FILENAME}")
        if num_albumless_pics:
            logger.info(
                f"An additional of {num_albumless_pics} photos weren't part of any album. Such "
                f"photos were copied to the directory '{self.ALBUMLESS_PICS_DIR}'."
            )
