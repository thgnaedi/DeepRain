# https://docs.wradlib.org/en/stable/installation.html
# ENABLE ENVIRONMENT FIRST!
# Environment Access via Anaconda Navigator

# Breitengrad von Konstanz: 47.6779496
# Längengrad von Konstanz: 9.1732384

import os
import wradlib as wrl
import numpy as np
import matplotlib.pyplot as pl
import warnings
import csv, fileinput


def read_radolan(radfile):
    radfile = wrl.util.get_wradlib_data_file('' + radfile)
    return wrl.io.read_radolan_composite(radfile)


def plot_radolan(data, attrs, grid, clabel=None):
    fig = pl.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, aspect='equal')
    x = grid[:, :, 0]
    y = grid[:, :, 1]
    pm = ax.pcolormesh(x, y, data, cmap='viridis')
    cb = fig.colorbar(pm, shrink=0.75)
    cb.set_label(clabel)
    pl.xlabel("x [km]")
    pl.ylabel("y [km]")
    pl.title('{0} Product\n{1}'.format(attrs['producttype'],
                                       attrs['datetime'].isoformat()))
    pl.xlim((x[0, 0], x[-1, -1]))
    pl.ylim((y[0, 0], y[-1, -1]))
    pl.grid(color='r')


def plot_radolan_png(data, attrs, grid, clabel=None, pathToSave='Unnamed'):
    fig = pl.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, aspect='equal')
    x = grid[:, :, 0]
    y = grid[:, :, 1]

    data = data[200:800, 200:850]
    x = x[200:800, 200:850]
    y = y[200:800, 200:850]

    pm = ax.pcolormesh(x, y, data, cmap='viridis')
    pl.axis('off')
    pl.xlim((x[0, 0], x[-1, -1]))
    pl.ylim((y[0, 0], y[-1, -1]))
    pl.savefig(os.environ["WRADLIB_DATA"] + '/' + pathToSave + '.png', bbox_inches='tight')


def min_max_from_array(data):
    mini = 99999999999
    maxi = 0
    for value in data:
        if value > maxi:
            maxi = value
        if value < mini:
            mini = value
    return mini, maxi


# Array-Like, minimum of all data, max of all data, bit depth of data-/image-type
def normalize(data, absolute_min, absolute_max, bitdepth=255):
    factor = bitdepth/absolute_max
    data -= absolute_min
    data *= factor
    return data


def query_metadata_file(filename):
    with open(filename, 'r') as infile:
        reader = csv.reader(infile, delimiter=",", quotechar='"')
        minimum = 999999999
        maximum = 0
        for row in reader:
            if len(row) == 0:
                continue
            if int(row[1]) < minimum:
                minimum = int(row[1])
            if int(row[2]) > maximum:
                maximum = int(row[2])

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


if __name__ == '__main__':
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

    # Path to DATA location (Change to match Crwaler )
    os.environ["WRADLIB_DATA"] = r"/data/Radarbilder_DWD/TEST"

    # Grid Germany (National Composites (R-, S- and W-series) <- USED)
    radolan_grid_xy = wrl.georef.get_radolan_grid(900, 900)
    # Extended Grid (As used in  European Composites)
    radolan_egrid_xy = wrl.georef.get_radolan_grid(1500, 1400)

    # Grid Germany+d
    radolan_wgrid_xy = wrl.georef.get_radolan_grid(1100, 900)

    # First pass: get min and max for all radolan files
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        for file in files:
            if '.png' in file:
                continue
            data, attrs = read_radolan(file)
            data = np.ma.masked_equal(data, -9999)

            current_min, current_max = min_max_from_array(data)
            update_metadata_file(metadata_file_name, [file, current_min, current_max])

    clean_csv(metadata_file_name)  # Removes duplicate entries

    # ToDo: 2nd pass - save scaled images with generated metadata
    abs_min, abs_max = query_metadata_file(metadata_file_name)
    for subdir, dirs, files in os.walk(os.environ["WRADLIB_DATA"]):
        for file in files:
            if '.png' in file:
                continue
            data, attrs = read_radolan(file)
            # Scale
            data = normalize(data, abs_min, abs_max)
            plot_radolan_png(data, attrs, radolan_grid_xy, clabel='mm * h-1', pathToSave=file)
