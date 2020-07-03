# Data processing
The radar data has to be converted to PNG files to be easily usable and further processed. More background informations can be found at the [Wiki-page](https://github.com/thgnaedi/DeepRain/wiki/Convert-radardata-to-pngs)

## DWD to PNG
The script ```DWDtoPNGScript.py``` converts the radar data from the DWD to PNG and spread the values to a range of 0 to 255 so that they can be saved as 8-bit PNGs.

To passes are needed for this process. While the first pass the minimum and maximum are determined, to scale the values correctly. The second pass actually converts the radar data to PNG files.

Also a CSV file will be created with the min and max of each radar data file. So the metadata computation can be skipped on the next run.

## Usage
The script must be run from command line and take at least two arguments: the directory with uncompressed radar data files ([DWD-Crawler Readme](https://github.com/thgnaedi/DeepRain/blob/master/DWD_Crawler/README.md)), and the directory where to save the PNG in.

Argument    | Bedeutung
------------|--------
-h          | Prints a help screen ith description nd command line options
-i \<dir\>  | Directory with uncompressed radar data
-o \<dir\>  | Directory where to save the PNG in
-q          | Quantile for maximum rainfall in PNG (e.g. 0.99 -> 1% of rainfall will be clipped)
-v          | Value (set the maximum value directly, skipping quantile calculation step)
