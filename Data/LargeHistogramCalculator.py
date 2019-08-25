# Hello to the Large Histogram Calculator
# This noteboook is supposed to calculate the histogram of a whole year
#
# It needs to iterate over all 5-minutely files,
# but must not keep all the values in RAM but instead computes a histogram
# with predefined bins for each file.
import argparse
import os
import glob
import numpy as np
import wradlib as wrl
import logging

from Data.DWDtoPngScript import query_metadata_file


# Logger
logger = logging.getLogger("Large Histogram Calculator")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("LHC.log")
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


# Constants
bin_file_name_prefix = "raa01-yw2017.002_10000-"
img_file_name_prefix = "scaled_"


def read_data_from_radolan(radfile):
    radfile = wrl.util.get_wradlib_data_file(radfile)
    data, attrs = wrl.io.read_radolan_composite(radfile)
    data = np.ma.masked_equal(data, -9999)
    return data


def get_filename_prefix(year):
    date_string_w_full_year = "{:4d}".format(year)
    return date_string_w_full_year[2:]


def main(data_directory, metadata_file_name, year=None):
    num_bins = 10

    year_begin = 2001
    year_end = 2017

    # Determine bins
    data_min, data_max = query_metadata_file(metadata_file_name)
    bins = np.linspace(data_min, data_max, num_bins)
    hist = np.zeros(num_bins - 1, dtype='int16')

    if year is not None:
        year_begin = year
        year_end = year + 1

    for year in range(year_begin, year_end+1):
        logger.info("Parsing year: {}".format(year))
        year_dir = data_directory + str(year) + "/"
        # Make wradlib stop complaining
        os.environ["WRADLIB_DATA"] = year_dir
        os.chdir(year_dir)

        # Compose complete historgram by singele histograms
        counter = 0
        filename_prefix = bin_file_name_prefix + get_filename_prefix(year)
        for file in glob.glob(filename_prefix + "*"):
            try:
                bin_data = read_data_from_radolan(file)
                bin_data_hist, _ = np.histogram(bin_data, bins)
                hist += bin_data_hist
                counter += 1
            except OSError as e:
                logger.error("Could not read file: " + str(e))
        logger.info("Processed {} files.".format(counter))
    logger.info("Number of values: {}".format(np.sum(hist)))
    np.save("LargeHistogram.npy", hist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Computes a histogram of the given year or all years. The maximum "
                                                 "must already be computed with DWD2PNG script in the same folder and "
                                                 "metadat file given with option! Use -h  for optinos!")
    parser.add_argument("-n", "--metadataFile",
                        dest="metadata_file",
                        help="Path to file with metadata of the radolan files.")
    parser.add_argument("-d", "--directory",
                        dest="data_directory",
                        help="Directory with the radonlan file to compute histogram from.")
    parser.add_argument("-y", "--year",
                        dest="year",
                        help="Specify the year to compute histogram from.")

    args = parser.parse_args()
    data_dir = "./" if args.data_directory is None else os.path.join(args.data_directory, '')
    logger.info("All Arguments initialized")

    main(data_directory=data_dir, metadata_file_name=args.metadata_file, year=args.year)
