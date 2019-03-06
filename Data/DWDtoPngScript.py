# https://docs.wradlib.org/en/stable/installation.html
# Breitengrad von Konstanz: 47.6779496
# Laengengrad von Konstanz: 9.1732384

# Computes a series of PNGs for the radolan datasets.
# Needs a 2-pass process, to determine MIN and MAX values in the first run,
# and generate normalized images in the second pass.
# The metadata (MIN/MAX, etc.) will be saved in a separate file,
# so that only new datasets need to be processed twice.

import os
import wradlib as wrl
import numpy as np
import warnings
import csv
import fileinput
import scipy.misc
import logging

logger = logging.getLogger("DWD to PNG (script)")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("dwd-to-png.log")
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


def read_radolan(radfile):
    radfile = wrl.util.get_wradlib_data_file(radfile)
    return wrl.io.read_radolan_composite(radfile)


def save_png_grayscale_8bit(image_data, filename):
    image_data_8bit = image_data.astype(np.uint8)
    full_filename = filename + ".png"
    scipy.misc.imsave(full_filename, image_data_8bit)
    logger.info("Saved image file: " + full_filename)


def min_max_from_array(data):
    mini = 99999999999
    maxi = 0
    for array in data:
        for value in array:
            if value > maxi:
                maxi = value
            if value < mini:
                mini = value
    return mini, maxi


# Array-Like, minimum of all data, max of all data, bit depth of data-/image-type
def normalize(data, absolute_min, absolute_max, bit_width=255):
    factor = bit_width/absolute_max
    data -= absolute_min
    data *= factor
    return data


def query_files_with_metadata(filename):
    filenames = []
    with open(filename, 'r') as infile:
        reader = csv.reader(infile, delimiter=",", quotechar='"')
        for row in reader:
            filenames.append(row[0])
    return filenames


def query_metadata_file(filename):
    with open(filename, 'r') as infile:
        reader = csv.reader(infile, delimiter=",", quotechar='"')
        minimum = 999999999
        maximum = 0
        for row in reader:
            if len(row) == 0:
                continue
            if float(row[1]) < minimum:
                minimum = float(row[1])
            if float(row[2]) > maximum:
                maximum = float(row[2])

    return minimum, maximum


def update_metadata_file(filename, new_data_set):
    with open(filename, 'a') as outfile:
        writer = csv.writer(outfile, delimiter=",")
        writer.writerow(new_data_set)


def clean_csv(filename):
    seen = set()
    for line in fileinput.FileInput(filename, inplace=1):
        if line in seen:
            continue
        seen.add(line)
        print(line)


def main():
    metadata_file_name = "radolan_metadata.csv"
    warnings.filterwarnings('ignore')

    # Path to DATA location (Change to match Crwaler )
    os.environ["WRADLIB_DATA"] = r"/data/Radarbilder_DWD/TEST"
    already_parsed_files = query_files_with_metadata(metadata_file_name)

    # First pass: get min and max for all radolan files
    counter = 0
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        for file in files:
            if '.png' in file:
                logger.info("Skipping png (" + str(counter)+'/'+str(len(files))+")")
                counter += 1
                continue
            if file in already_parsed_files:
                logger.info("Metadata already present for file: " + subdir + '/' + file
                            + " (" + str(counter)+'/'+str(len(files))+")")
                counter += 1
                continue
            data, attrs = read_radolan(subdir + '/' + file)
            data = np.ma.masked_equal(data, -9999)

            current_min, current_max = min_max_from_array(data)
            logger.info("Computed metadata from file: " + subdir + '/' + file)
            update_metadata_file(metadata_file_name, [file, current_min, current_max])
            logger.info("Wrote metadata for file: " + subdir + '/' + file + " (" + str(counter)+'/'+str(len(files))+")")
            counter += 1

    clean_csv(metadata_file_name)  # Removes duplicate entries
    logger.info("Cleaned metadata file: " + metadata_file_name)

    # 2nd pass - save scaled images with generated metadata
    counter = 0
    abs_min, abs_max = query_metadata_file(metadata_file_name)
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        for file in files:
            image_file_path = subdir + '/' + "scaled_" + file
            if '.png' in file:
                logger.info("Skipping png (" + str(counter)+'/'+str(len(files))+")")
                counter += 1
                continue
            if os.path.isfile(image_file_path + ".png"):
                continue
            data, attrs = read_radolan(subdir + '/' + file)
            # Scale
            data = normalize(data, abs_min, abs_max)
            logger.info("Normalized file: " + image_file_path + " (" + str(counter)+'/'+str(len(files))+")")
            save_png_grayscale_8bit(data, image_file_path)
            counter += 1


if __name__ == '__main__':
    main()
