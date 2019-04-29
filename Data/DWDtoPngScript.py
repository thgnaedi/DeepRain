# https://docs.wradlib.org/en/stable/installation.html
# Breitengrad von Konstanz: 47.6779496
# Laengengrad von Konstanz: 9.1732384

# Computes a series of PNGs for the radolan datasets.
# Needs a 2-pass process, to determine MIN and MAX values in the first run,
# and generate normalized images in the second pass.
# The metadata (MIN/MAX, etc.) will be saved in a separate file,
# so that only new datasets need to be processed twice.

import argparse
import os
import wradlib as wrl
import numpy as np
import warnings
import csv
import fileinput
import cv2
import logging


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


def get_maximum_for_file(path_to_file):
    (file, current_min, current_max) = get_metadata_for_file(path_to_file)
    return current_max


def get_maximum_for_file_generator(path_to_file):
    (file, current_min, current_max) = get_metadata_for_file(path_to_file)
    yield current_max


def get_metadata_for_file(path_to_file):
    global counter_files
    file = os.path.basename(path_to_file)
    path = os.path.dirname(path_to_file)

    data, attrs = read_radolan(path + '/' + file)
    data = np.ma.masked_equal(data, -9999)
    current_min = 0
    current_max = data.max()
    counter_files += 1
    logger.info("Computed metadata for file: " + path + '/' + file + " (" + str(counter_files)+'/'+str(total_files)+")")
    return [file, current_min, current_max]


def read_radolan(radfile):
    radfile = wrl.util.get_wradlib_data_file(radfile)
    return wrl.io.read_radolan_composite(radfile)


def save_png_grayscale_8bit(image_data, filename):
    image_data_8bit = image_data.astype(np.uint8)
    full_filename = filename + ".png"
    cv2.imwrite(full_filename, image_data_8bit)
    logger.info("Saved image file: " + full_filename)


# Array-Like, max of all data
def normalize(data, absolute_max):
    factor = float(255)/absolute_max
    data *= factor
    return data


def query_files_with_metadata(filename):
    filenames = []

    if not os.path.isfile(filename):
        return filenames

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


def update_metadata_file(metadata_file_name, new_row_entry):
    with open(metadata_file_name, 'a') as outfile:
        writer = csv.writer(outfile, delimiter=",")
        writer.writerow(new_row_entry)


def update_metadata_file_with_max(metadata_file_name, parsed_file_name, parsed_file_max):
    values_to_write = [parsed_file_name, 0, parsed_file_max]
    update_metadata_file(metadata_file_name, values_to_write)


def update_metadata_file_multiple_entries(metadata_file_name, new_row_entries_list):
    with open(metadata_file_name, 'a') as outfile:
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

    parser = argparse.ArgumentParser(
        description="Reads radolan files in one directory, scales them and saves them as PNG files in a directory")
    parser.add_argument("-i", "--inputDir",
                        dest="in_directory",
                        help="Target directory for downloads.")
    parser.add_argument("-o", "--outputDir",
                        dest="out_directory",
                        help="Target directory for binary files.")

    args = parser.parse_args()
    print("Parsed arguments:")
    in_dir = "./" if args.in_directory is None else args.in_directory
    out_dir = "./" if args.out_directory is None else args.out_directory
    print("DWD data directory: " + str(in_dir))
    print("PNG image directory: " + str(out_dir))

    # Path to DATA location (Change to match Crwaler)
    os.environ["WRADLIB_DATA"] = in_dir
    already_parsed_files = query_files_with_metadata(metadata_file_name)

    # First pass: get min and max for all radolan files
    files_to_be_parsed = []
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        total_files += len(files)
        for file in files:
            if '.png' in file:
                logger.info("Skipping png (" + str(counter_files)+'/'+str(len(files))+")")
                total_files -= 1
                continue
            if file in already_parsed_files:
                total_files -= 1
                continue

            # Add filenames to be parsed to list
            files_to_be_parsed.append(subdir + '/' + file)

    print("Files to parse: " + str(len(files_to_be_parsed)))

    # Make cool dictionary comprehension
    max_dict = {name: get_maximum_for_file_generator(name) for name in files_to_be_parsed}

    # Write all metadata to file
    for (file, file_max) in max_dict:
        update_metadata_file_with_max(metadata_file_name, file, file_max)

    clean_csv(metadata_file_name)  # Removes duplicate entries
    logger.info("Cleaned metadata file: " + metadata_file_name)

    # 2nd pass - save scaled images with generated metadata
    total_files = 0
    counter = 0
    abs_min, abs_max = query_metadata_file(metadata_file_name)
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        total_files += len(files)
        for file in files:
            image_file_path = out_dir + '/' + "scaled_" + file
            if '.png' in file:
                logger.info("Skipping png (" + str(counter)+'/'+str(len(files))+")")
                total_files -= 1
                continue
            if os.path.isfile(image_file_path + ".png"):
                total_files -= 1
                continue
            data, attrs = read_radolan(subdir + '/' + file)

            data = normalize(data, abs_max)  # Scale
            logger.info("Normalized file: " + image_file_path + " (" + str(counter)+'/'+str(len(files))+")")
            save_png_grayscale_8bit(data, image_file_path)
            counter += 1


if __name__ == '__main__':
    main()
