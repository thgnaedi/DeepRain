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

from multiprocessing import Pool


counter_files = 0
total_files = 0

logger = logging.getLogger("DWD to PNG (script)")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("dwd-to-png.log")
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


def get_metadata_for_file(path_to_file):
    global counter_files
    # ToDo: Split filename and path
    file = os.path.basename(path_to_file)
    path = os.path.dirname(path_to_file)

    data, attrs = read_radolan(path + '/' + file)
    data = np.ma.masked_equal(data, -9999)
    current_min, current_max = min_max_from_array(data)
    counter_files += 1
    logger.info("Computed metadata for file: " + path + '/' + file + " (" + str(counter_files)+'/'+str(total_files)+")")
    return [file, current_min, current_max]


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
            if len(row) > 0:
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


def update_metadata_file(filename, new_row_entry):
    with open(filename, 'a') as outfile:
        writer = csv.writer(outfile, delimiter=",")
        writer.writerow(new_row_entry)


def update_metadata_file_multiple_entries(filename, new_row_entries_list):
    with open(filename, 'a') as outfile:
        writer = csv.writer(outfile, delimiter=",")
        for row in new_row_entries_list:
            writer.writerow(row)


def clean_csv(filename):
    seen = set()
    for line in fileinput.FileInput(filename, inplace=1):
        if line in seen:
            continue
        seen.add(line)
        print(line)


def main():
    global counter_files, total_files
    metadata_file_name = "radolan_metadata.csv"
    warnings.filterwarnings('ignore')

    # Path to DATA location (Change to match Crwaler )
    os.environ["WRADLIB_DATA"] = r"/data/Radarbilder_DWD/minutely/june"
    already_parsed_files = query_files_with_metadata(metadata_file_name)

    # First pass: get min and max for all radolan files
    files_to_be_parsed = []
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        total_files += len(files)
        for file in files:
            if '.png' in file:
                logger.info("Skipping png (" + str(counter_files)+'/'+str(len(files))+")")
                counter_files += 1
                continue
            if file in already_parsed_files:
                counter_files += 1
                continue

            # Add filenames to be parsed to list
            files_to_be_parsed.append(subdir + '/' + file)

    print("Files to parse: " + str(len(files_to_be_parsed)))
    # Start Pool
    with Pool(8) as p:
        result_list = p.map(get_metadata_for_file, files_to_be_parsed)

    # Write all metadata to file
    update_metadata_file_multiple_entries(metadata_file_name, result_list)

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
