#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mimetypes
import os
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import img_as_ubyte
from skimage.filters import rank
from skimage.filters import threshold_otsu
from skimage.io import imread
from skimage.io import imsave
from skimage.morphology import disk


def mkdir(folderpath):
    """Creates a folder for the specified 'folderpath'.

    Input:
        folderpath: string path

    Raises:
        ValueError: If 'folderpath' can not be created due to PermissionError
    """

    path = Path(folderpath)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError as error:
        raise ValueError(
            f"Please adapt permissions to create {folderpath} or choose a different directory."
        ) from error


def list_filenames(path):
    """Given a path, lists all image(s) within the path. The input path can
    either be (i) a directory in which case all the images will be listed in
    the dictionary, or (ii) an image file.

    Returns:
        filenames: A list with all filenames
    """

    ## Get filenames
    filenames = []
    if os.path.isdir(path):
        print(f"Images in '{path}' will be loaded")
        for file in os.listdir(path):
            (filetype, _) = mimetypes.guess_type(file)
            if filetype and "image" in filetype:
                filenames.append(os.path.basename(file))
    else:
        filenames.append(os.path.basename(path))
    print(f"{len(filenames)} images found in '{path}'")
    return filenames


def load_imgs(path, filenames):
    """Given a path, loads image(s). The input path can either be (i) a
    directory in which case all the JPG-images will be loaded into a
    dictionary, or (ii) an image file.

    Returns:
        imgs: A dictionary of of n-dim images. Keys are the original filenames
    """

    def load_image(file):
        img_data = None
        try:
            img_data = imread(os.path.join(path, file))
        except ValueError:
            print(f"'{file}' was unfortunately not an image. Skipping this one.")
        return img_data

    ## Load images
    imgs = {}
    if isinstance(filenames, list):
        for file in filenames:
            print(f"\nImage: '{file}'")
            imgs[file] = load_image(file)
            print("Done")
    elif isinstance(filenames, str):
        imgs[filenames] = load_image(filenames)
    else:
        raise ValueError(
            "Argument is an unexpected type. Only lists and strings are supported"
        )
    return imgs


def save_img(img, filename):
    """Given a numpy array image save image under filename."""

    mkdir(os.path.dirname(filename))
    imsave(filename, img)


def resize(img, size=(400, 400), resample=Image.BILINEAR):
    return np.asarray(Image.fromarray(np.uint8(img)).resize(size, resample))


def rgb2gray(img):
    """Given an RGB image return the gray scale image.

    Based on http://en.wikipedia.org/wiki/Grayscale#Converting_color_to_grayscale
    img = 0.299 R + 0.587 G + 0.114 B
    """

    print("Convert RGB image to gray scale.")
    return np.uint8(np.dot(img[..., :3], [0.299, 0.587, 0.114]))


def gauss_filter(img, sigma=4, mode="nearest"):
    print(f"Smooth image using a Gaussian kernel sigma {sigma}")
    # h, w = img.shape
    # return ndimage.filters.gaussian_filter(img, sigma=[sigma*(400/w), sigma*(400/h)], mode=mode)
    return ndimage.filters.gaussian_filter(img, sigma=sigma, mode=mode)


def median_filter(img, size=4):
    print(f"Smooth image using a median filter size {size}")
    return ndimage.filters.median_filter(img, size)


def threshold_img(img, method="global_otsu", radius=50):
    """Given a gray scale image return a thresholded binary image using Otsu's
    thresholding method.

    Input:
        img: A gray scale numpy array.
        method:
          - 'global_otsu' computes a global threshold value for the whole image and
            uses this to binarize the input image. (default)
          - 'local_otsu' computes a local threshols value for each pixel
            (threshold is computed within a neighborhood of a radius).
        radius: The 2D neighborhood to compute local thresholds in local_otsu method

    Returns:
        img_binary: A binary image (same size as input img).
        threshold: Threshold value used to binarize the image.
    """

    if len(img.shape) > 2:
        img = rgb2gray(img)

    if method == "global_otsu":
        threshold = threshold_otsu(img)
        img_binary = img >= threshold

    elif method == "local_otsu":
        selem = disk(radius)
        threshold = rank.otsu(img, selem)
        img_binary = img >= threshold

    return img_as_ubyte(img_binary), threshold
