"""
Set of generic helpers.
"""
import re
import unicodedata
from typing import List


def normalize(value: str, allow_unicode: bool = True):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces/dashes to underscores.
    """
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")

    # Remove non-alpha numerics except chars '/\-'
    value = re.sub(r"[^\w\s\/\\-]", "", value).strip().lower()
    # Translate chars '\/' to "-"
    value = re.sub(r"[\/\\]", "-", value)
    # Translates '-' and ' ' to '_'
    return re.sub(r"[-\s]+", "_", value)


def find_duplicates(files_sets: List[set]) -> set:
    """
    Finds all duplicate files in `files_sets`.

    :param files_sets: All subsets of files.
    :return: Duplicate files.
    """
    duplicates: set = set()
    for i, target_files in enumerate(files_sets):
        for j, subset in enumerate(files_sets):
            if i == j:
                continue
            duplicates = duplicates | (target_files & subset)

    return duplicates
