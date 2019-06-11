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


def get_maximum_for_file(path_to_file):
    (file, current_min, current_max) = get_metadata_for_file(path_to_file)
    return current_max


def get_maximum_for_file_generator(file_list):
    for path_to_file in file_list:
        try:
            (file, current_min, current_max) = get_metadata_for_file(path_to_file)
            yield (file, current_max)
        except Exception:
            logger.error("File corrupt: " + path_to_file)


def get_metadata_for_file(path_to_file):
    global counter_files
    file = os.path.basename(path_to_file)
    path = os.path.dirname(path_to_file)

    data, attrs = read_radolan(path + '/' + file)
    data = np.ma.masked_equal(data, -9999)
    current_min = 0
    current_max = data.max()
    counter_files += 1
    logger.info("Computed metadata for file: " + path+'/'+file+" ("+str(counter_files)+'/'+str(total_files)+")")
    return [file, current_min, current_max]


def read_radolan(radfile):
    radfile = wrl.util.get_wradlib_data_file(radfile)
    return wrl.io.read_radolan_composite(radfile)


def save_png_grayscale_8bit(image_data, filename, factor=1):
    image_data_8bit = image_data.astype(np.uint8)
    image_data_8bit *= int(factor)
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
    os.rename(filename, filename + ".BAK")

    num_unique_lines = 0
    num_total_lines = 0
    seen = set()
    with open(filename + ".BAK", 'r') as in_file, open(filename, 'w') as out_file:
        for line in in_file:
            num_total_lines += 1
            if line in seen:
                continue
            num_unique_lines += 1
            seen.add(line)
            out_file.write(line)
    logger.info("Cleanup metadata: {} unique entries, {} entries removed"
                .format(num_unique_lines, num_total_lines - num_unique_lines))


def get_timestamp_for_bin_filename(bin_file_name):
    split = bin_file_name.split('-')
    timestamp = split[2]
    return timestamp


def main(in_dir, out_dir, metadata_file="radolan_metadata.csv", no_metadata=False, factor=1):
    global counter_files, total_files
    warnings.filterwarnings('ignore')

    # Path to DATA location (Change to match Crwaler)
    os.environ["WRADLIB_DATA"] = in_dir

    # First pass: get min and max for all radolan files
    if not no_metadata:
        already_parsed_files = query_files_with_metadata(metadata_file)

        files_to_be_parsed = []
        for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
            total_files += len(files)
            for file in files:
                if '.png' in file:
                    logger.info("Skipping png (" + str(counter_files) + '/' + str(len(files)) + ")")
                    total_files -= 1
                    continue
                if file in already_parsed_files:
                    total_files -= 1
                    continue

                # Add filenames to be parsed to list
                files_to_be_parsed.append(subdir + '/' + file)

        logger.info("Files to parse: " + str(len(files_to_be_parsed)))

        # Make cool generator for lazy evaluation!
        generator = get_maximum_for_file_generator(files_to_be_parsed)

        # Write all metadata to file
        for file, file_max in generator:
            update_metadata_file_with_max(metadata_file, file, file_max)

        clean_csv(metadata_file)  # Removes duplicate entries
        logger.info("Cleaned metadata file: " + metadata_file)

    # 2nd pass - save scaled images with generated metadata
    total_files = 0
    counter = 0
    abs_min, abs_max = query_metadata_file(metadata_file)
    logger.info("Minimum: {} / Maximum: {}".format(abs_min, abs_max))

    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        total_files += len(files)
        for file in files:
            image_file_path = out_dir + '/' + "scaled_" + get_timestamp_for_bin_filename(file)
            if '.png' in file:
                logger.info("Skipping png (" + str(counter)+'/' + str(len(files)) + ")")
                total_files -= 1
                continue
            if os.path.isfile(image_file_path + ".png"):
                total_files -= 1
                continue
            data, attrs = read_radolan(subdir + '/' + file)

            data = normalize(data, abs_max)
            save_png_grayscale_8bit(data, image_file_path, factor)
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
    parser.add_argument("-m", "--metadataFile",
                        dest="metadata_file",
                        help="Specify the file to save and load metadata.")
    parser.add_argument("-n", "--not-compute-metadata",
                        dest="not_compute_metadata",
                        help="Does not compute metadata for new files, but reads only metadata from given file.",
                        action="store_true")
    parser.add_argument("-c", "--compute-metadata",
                        dest="compute_metadata",
                        help="Explicitly compute metadata for new files.",
                        action="store_true")
    parser.add_argument("-f", "--factor",
                        dest="factor",
                        help="Specify a factor to multiply with each data element.")

    args = parser.parse_args()
    logger.info("Parsed arguments:")
    in_dir = "./" if args.in_directory is None else args.in_directory
    out_dir = "./" if args.out_directory is None else args.out_directory
    logger.info("DWD data directory: {}".format(str(in_dir)))
    logger.info("PNG image directory: {}".format(str(out_dir)))
    logger.info("Metadata file: {}".format(str(args.metadata_file)))
    if args.not_compute_metadata:
        logger.info("Not compute Metadata!")
    else:
        logger.info("Compute Metadata")

    # Test if arguments are valid
    if not os.path.isdir(in_dir):
        logger.error("Input directory is not valid: Aborting!")
        sys.exit(-1)
    if not os.path.isdir(out_dir):
        logger.error("Output directory is not valid: Aborting!")
        sys.exit(-1)
    if not os.path.isfile(args.metadata_file) and args.not_compute_metadata:
        logger.error("No valid metadata file given and should not compute metadata: Aborting!")
        sys.exit(-1)
    if args.not_compute_metadata and args.compute_metadata:
        logger.error("To compute and not to compute metadata?!? Aborting!!!")
        sys.exit(-1)
    if args.factor is not None and is_number(args.factor):
        logger.error("Factor is not a valid number: {} !!! Aborting!!!".format(args.factor))
        sys.exit(-1)

    if args.factor is None:
        main(in_dir, out_dir, args.metadata_file, args.not_compute_metadata)
    else:
        main(in_dir, out_dir, args.metadata_file, args.not_compute_metadata, args.factor)
