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
import sys
import wradlib as wrl
import numpy as np
import warnings
import csv
import cv2
import logging


counter_files = 0
total_files = 0


logger = logging.getLogger("DWD to PNG (script)")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("dwd-to-png.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

#ToDo unused and remove? or used in a notebook?
def get_maximum_for_file(path_to_file):
    return get_metadata_for_file(path_to_file, onlyMax=True)


def get_quantile_from_distribution(file_list, quantile=1, nameHist=None):
    if quantile > 1:
        quantile = 1
    global_hist = None      # Histogram over all files
    global_edges = None     # edges of the histogram

    #compute hist for every file and add to global hist
    for path_to_file in file_list:
        try:
            file, hist, binedges, current_max = get_metadata_for_file(path_to_file)
            if current_max < 0:
                # broken or empty file (no radar station)
                os.remove(path_to_file)
                continue
            if(global_edges is None):
                global_edges = binedges
                global_hist = hist
            else:
                global_hist += hist
        except Exception as e:
            logger.error("File corrupt: " + path_to_file + str(e))

    # collected all informations, now calc scale info:

    if nameHist is not None:
        logger.info("store Histogram in " + str(nameHist))
        np.save(str(nameHist), global_hist)

    global_hist[0:5] = 0  #ignore no/nearby no rain
    n_values_to_cover = global_hist.sum()*quantile
    n_covered_values = 0

    #ToDo: globales File speichern mit quantilen?
    for i in range(len(global_hist)):
        n_covered_values += global_hist[i]
        if n_covered_values >= n_values_to_cover:
            return global_edges[i+1] # right side of current bin
    logger.error("this line should never be reached?!?, continue")
    return global_edges[-1] # maximum of histogram


def get_metadata_for_file(path_to_file, onlyMax=False):
    global counter_files
    file = os.path.basename(path_to_file)
    path = os.path.dirname(path_to_file)

    data, attrs = read_radolan(path + '/' + file)
    current_max = data.max()
    if onlyMax:
        return current_max

    hist, binedges = np.histogram(data, bins=500, range=(0,5))

    counter_files += 1
    if(counter_files%50 == 0):
        logger.info("Computed metadata for file: " + path+'/'+file+" ("+str(counter_files)+'/'+str(total_files)+")")

    return file, hist, binedges, current_max


def read_radolan(radfile):
    radfile = wrl.util.get_wradlib_data_file(radfile)
    return wrl.io.read_radolan_composite(radfile)


def save_png_grayscale_8bit(image_data, filename, factor=1):
    global counter_files

    image_data_8bit = image_data.astype(np.uint8)
    image_data_8bit *= int(factor)
    full_filename = filename + ".png"
    cv2.imwrite(full_filename, image_data_8bit)
    counter_files += 1
    if(counter_files % 50 == 0):
        logger.info("({}/{}) Saved image file: {}".format(counter_files, total_files, full_filename))

# Array-Like, max of all data
def normalize(data, absolute_max):
    MAXVALUE = float(255)
    factor = MAXVALUE/absolute_max
    data *= factor
    data[data > MAXVALUE] = MAXVALUE
    return data

def get_timestamp_for_bin_filename(bin_file_name):
    if(not bin_file_name.endswith("---bin")):   #ignore archive files or previously created images
        logger.info("skipping file: {}".format(bin_file_name))
        return None
    split = bin_file_name.split('-')
    timestamp = split[2]
    return timestamp


# ToDo: remove unused parameters (metadatafile etc.)
def main(in_dir, out_dir, quantile, maximum_value=None, nameHist=None):
    global counter_files, total_files
    warnings.filterwarnings('ignore')

    quantile = float(quantile)

    # Path to DATA location (Change to match Crwaler)
    os.environ["WRADLIB_DATA"] = in_dir


    # First pass: get max value with quantile and probability distribution (if not given as parameter)
    if maximum_value is None:

        files_to_be_parsed = []
        # collect all files to parse
        for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
            total_files += len(files)
            for file in files:
                if '.png' in file:
                    logger.info("Skipping png (" + str(counter_files) + '/' + str(len(files)) + ")")
                    total_files -= 1
                    continue
                # Add filenames to be parsed to list
                files_to_be_parsed.append(subdir + '/' + file)

        logger.info("Files to parse: " + str(len(files_to_be_parsed)))

        # get maximum value from histogram
        maximum_value = get_quantile_from_distribution(files_to_be_parsed, quantile=quantile, nameHist=nameHist)

    else:
        maximum_value = float(maximum_value)


    total_files = 0
    counter = 0
    abs_min = 0
    abs_max = maximum_value

    logger.info("Minimum: {} / Maximum: {}".format(abs_min, abs_max))

    counter_files = 0

    # 2nd pass - save scaled images with generated metadata
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        total_files += len(files)
        for file in files:
            timestamp = get_timestamp_for_bin_filename(file)
            if timestamp is None:   # not a binary file, maybe archive file or image found
                continue

            image_file_path = os.path.join(out_dir, "scaled_" + timestamp)
            if '.png' in file:
                logger.info("Skipping png (" + str(counter)+'/' + str(len(files)) + ")")
                total_files -= 1
                continue
            if os.path.isfile(image_file_path + ".png"):
                total_files -= 1
                continue
            data, attrs = read_radolan(subdir + '/' + file)

            data = normalize(data, abs_max)
            save_png_grayscale_8bit(data, image_file_path)
            counter += 1


def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Reads radolan files in one directory, scales them and saves them as PNG files in a directory")
    parser.add_argument("-i", "--inputDir",
                        dest="in_directory",
                        help="Directory with binary DWD files to be converted.")
    parser.add_argument("-o", "--outputDir",
                        dest="out_directory",
                        help="Target directory for PNG files.")
    parser.add_argument("-q", "--quantile",
                        dest="quantile",
                        help="Specify a quantile to calc the max value")
    parser.add_argument("-v", "--value",
                        dest="value",
                        help="Specify the maximum value for rainfall (this value will be scaled to 255 in the output image)")
    parser.add_argument("-n", "--nameHist",
                        dest="nameHist",
                        help="Name for the file in wich the calculated histogram should be stored")

    args = parser.parse_args()
    logger.info("Parsed arguments:")
    in_dir = "./" if args.in_directory is None else args.in_directory
    out_dir = "./" if args.out_directory is None else args.out_directory
    logger.info("DWD data directory: {}".format(str(in_dir)))
    logger.info("PNG image directory: {}".format(str(out_dir)))
    if(args.nameHist is not None and args.value is None):
        logger.info("Store calculated histogram in"+str(args.nameHist))

    # Test if arguments are valid
    if(args.quantile is not None and is_number(args.quantile)):
        logger.info("Quantile: {}".format(args.quantile))
    else:
        logger.info("using default quantile = 1.0 -> all Data will be used")
        args.quantile = "1"
    if not os.path.isdir(in_dir):
        logger.error("Input directory is not valid: Aborting!")
        sys.exit(-1)
    if not os.path.isdir(out_dir):
        logger.error("Output directory is not valid: Aborting!")
        sys.exit(-1)

    #in_dir, out_dir, quantile, metadata_file="radolan_metadata.csv", no_metadata=False, factor=1, maximum_value=None
    main(in_dir, out_dir, args.quantile, args.value, args.nameHist)
