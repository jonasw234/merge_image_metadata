#!/usr/bin/env python3
"""
Merge metadata between images.
Useful for cases when metadata was already added and then you receive the high-res
version afterwards.
Assumes that you want to merge the Keyword, Subject, and HierarchicalSubject fields as
used by Adobe Bridge.
Currently merges metadata between two consecutive images only (i.e. will not correctly
detect triplicates).

Usage: merge_image_metadata.py [-v] FOLDER

Options:
    -v  Enable verbose (debug) output
"""
import logging
import os
import subprocess
import sys
from typing import Callable, Tuple

import imagehash
from PIL import Image

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def create_image_hash(
    image_path: str, algorithm: Callable = imagehash.average_hash
) -> imagehash.ImageHash:
    """
    Create a perceptual hash for an image file.

    Parameters
    ----------
    image_path : str
        Path to the image
    algorithm : Callable
        The algorithm to use to hash the image file.
        `imagehash.average_hash` is great for similar images
        (https://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html)

    Returns
    -------
    imagehash.ImageHash
        The image hash for the image
    """
    return algorithm(Image.open(image_path))


def compare_image_hashes(
    image1_hash: imagehash.ImageHash,
    image2_hash: imagehash.ImageHash,
    max_difference: int = 1,
) -> bool:
    """
    Compare two image hashes and return True if they are similar.

    Parameters
    ----------
    image1_hash : imagehash.ImageHash
        The hash of the first image
    image2_hash : imagehash.ImageHash
        The hash of the second image
    max_difference : int
        Images have to be at maximum this different to be considered the same

    Returns
    -------
    bool
        True if the images are close enough to be considered the same
    """
    return image1_hash - image2_hash <= max_difference


def merge_metadata(image1_path: str, image2_path: str) -> Tuple[list, list, list]:
    """
    Merge two images metadata into a single string.

    Parameters
    ----------
    image1_path : str
        Path to the first image
    image2_path : str
        Path to the second image

    Returns
    -------
    Tuple[list, list, list]
        A tuple of the merged keywords, subjects, and hierarchical subjects
    """
    base_command = [
        "exiftool",
        "-L",  # Don’t convert encodings
        "-charset",
        "filename=cp1252",  # For Windows file paths
        "-Keywords",
        "-Subject",
        "-HierarchicalSubject",
    ]

    keywords = []
    subject = []
    hierarchicalsubject = []

    for file in (image1_path, image2_path):
        exiftool_command = base_command.copy()
        exiftool_command.append(file)
        output = subprocess.check_output(exiftool_command).decode()
        try:
            keywords.append(output.split("\r\n", 1)[0].split(": ")[1])
            subject.append(output.split("\r\n")[1].split(": ")[1])
            hierarchicalsubject.append(output.split("\r\n")[2].split(": ")[1])
        except IndexError:
            continue

    keywords_list = list(set((", ".join(keywords)).split(", ")))
    logger.debug(
        "Combined keywords of %s and %s: %s",
        image1_path,
        image2_path,
        ", ".join(keywords_list),
    )
    subject_list = list(set((", ".join(subject)).split(", ")))
    hierarchicalsubject_list = list(set((", ".join(hierarchicalsubject)).split(", ")))

    return (keywords_list, subject_list, hierarchicalsubject_list)


def apply_metadata(
    image_path: str, keywords: list, subjects: list, hierarchicalsubjects: list
) -> None:
    """
    Apply new metadata to an image.

    Parameters
    ----------
    image_path : str
        The path to the image to which the metadata should be applied
    keywords : list
        The keywords for the image
    subjects : list
        The subjects for the image
    hierarchicalsubjects : list
        The hierarchical subjects for the image
    """
    parameters = [
        "exiftool",
        "-overwrite_original",
        "-L",  # Don’t convert encodings
        "-charset",
        "filename=cp1252",  # For Windows file paths
    ]
    parameters.extend([f"-Keywords+={keyword}" for keyword in keywords])
    parameters.extend([f"-Subject+={subject}" for subject in subjects])
    parameters.extend(
        [
            f"-HierarchicalSubject+={hierarchicalsubject}"
            for hierarchicalsubject in hierarchicalsubjects
        ]
    )
    parameters.append(image_path)
    logger.info(
        "Adding the following keywords (and related subjects and hierarchical subjects) "
        "to %s: %s",
        image_path,
        ", ".join(keywords),
    )

    subprocess.run(
        parameters,
        check=True,
    )


def compare_all_images(folder_path: str) -> None:
    """
    Compare all images in the given folder and transfer metadata between similar
    images.

    Parameters
    ----------
    folder_path : str
        Path to the folder containing the images.
    """
    logger.debug("Finding all image files in %s", folder_path)
    image_files = [
        f for f in os.listdir(folder_path) if f.lower().endswith(IMAGE_EXTENSIONS)
    ]

    # 1. Create image hashes and save them in a dictionary
    logger.debug("Calculating perceptual hashes for image files ...")
    image_dict = {
        os.path.join(folder_path, image_file): create_image_hash(
            os.path.join(folder_path, image_file)
        )
        for image_file in image_files
    }

    # 2. Compare all image hashes in the dictionary
    logger.debug("Comparing the hashes and finding duplicates ...")
    for image1, hash1 in image_dict.items():
        for image2, hash2 in image_dict.items():
            if image1 < image2:  # Compare only unique pairs of images
                if compare_image_hashes(hash1, hash2):
                    logger.debug(
                        "%s and %s seem to be similar. Merging their metadata.",
                        image1,
                        image2,
                    )
                    # 3. Merge the metadata of all images where the perceptual hashes
                    # are similar
                    keywords, subjects, hierarchicalsubject = merge_metadata(
                        image1, image2
                    )
                    # 4. Write the merged metadata for each image
                    for image in (image1, image2):
                        apply_metadata(image, keywords, subjects, hierarchicalsubject)


def main() -> None:
    """Main function to run the script."""
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(1)
    folder = ""
    for arg in sys.argv[1:]:
        if arg == "-v":
            logger.setLevel(logging.DEBUG)
        else:
            folder = arg
    compare_all_images(folder)


if __name__ == "__main__":
    main()
