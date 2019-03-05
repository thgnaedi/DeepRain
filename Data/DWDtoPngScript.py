# https://docs.wradlib.org/en/stable/installation.html
# ENABLE ENVIRONMENT FIRST!
# Environment Access via Anaconda Navigator

# Breitengrad von Konstanz: 47.6779496
# Laengengrad von Konstanz: 9.1732384

import os
import wradlib as wrl
import numpy as np
import warnings
import csv
import fileinput
import scipy.misc


def read_radolan(radfile):
    radfile = wrl.util.get_wradlib_data_file(radfile)
    return wrl.io.read_radolan_composite(radfile)


def save_png_grayscale_16bit(image_data, filename):
    # Convert to 16 bit depth
    image_data_8bit = image_data.astype(np.uint8)

    # Save
    full_filename = os.environ["WRADLIB_DATA"] + filename + ".png"
    scipy.misc.imsave(full_filename, image_data_8bit)


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
    # { "filename" : {"min":1, "max":245}, "file2": {"min":2, "max":250}, ... }

    # Parameters: xStart, xEnd, yStart, yEnd (used to crop the images to a certain size)
    # Maybe also use real coordinates to specify area

    # Computes a series of PNGs for the radolan datasets.
    # Needs a 2-pass process, to determine MIN and MAX values in the first run,
    # and generate normalized images in the second pass.
    # The metadata (MIN/MAX, etc.) will be saved in a separate file,
    # so that only new datasets need to be processed twice.

    warnings.filterwarnings('ignore')

    #test_path = "C:\\Users\\Eti\\git\\DeepRain\\Data\\data"

    # Path to DATA location (Change to match Crwaler )
    os.environ["WRADLIB_DATA"] = r"/data/Radarbilder_DWD/TEST"
    #os.environ["WRADLIB_DATA"] = test_path

    already_parsed_files = query_files_with_metadata(metadata_file_name)

    # First pass: get min and max for all radolan files
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        for file in files:
            if '.png' in file:
                continue
            if file in already_parsed_files:
                continue
            data, attrs = read_radolan(file)
            data = np.ma.masked_equal(data, -9999)

            current_min, current_max = min_max_from_array(data)
            update_metadata_file(metadata_file_name, [file, current_min, current_max])

    clean_csv(metadata_file_name)  # Removes duplicate entries

    # 2nd pass - save scaled images with generated metadata
    abs_min, abs_max = query_metadata_file(metadata_file_name)
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        for file in files:
            if '.png' in file:
                continue
            data, attrs = read_radolan(subdir + '/' + file)
            # Scale
            data = normalize(data, abs_min, abs_max)
            save_png_grayscale_16bit(data, os.environ["WRADLIB_DATA"] + '/' + "scaled_" + file)


if __name__ == '__main__':
    main()
