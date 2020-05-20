# DWD-Crawler
This folder contains a crawler to download the radar data from the DWD and unpacks it into a directory. There are arcives with files of a resolution of one hour and with 5 minutes. By default, the crawler downloads radar files that have the resolution of one hour.

Especially the archives of 5 minute resolution unpack to a lot of files (12x24x360 = 103680 files/year => roughly 90 GB/year for minutely files). So it is recommended that the output directory is on a large disk (>= 2TB) or on a file system that supports on-the-fly transparent compression (i.e. Btrfs); in the latter case a disk with 500GB should suffice.

## Usage
You must pass the download and output folder as arguments with ```-z``` and ```-o``` respectively.

You can either only download files or only uncompress already downloaded files with ```-d``` and ```-u``` respectively. When only downloading the output directory is ignored; when decompressing, both directories must be passed (to downloaded archives and output directory).

By default the archives with 1-hour resolution file are downloaded; with ```-m``` the archives with 5 minutes resolution will be downloaded.

Normally all available years will be downloaded, with ```-y``` and a number only archives of that year will be downloaded (don't try year 1002 ;).

Argument      | Action
--------------|--------
-h            | Prints a help screen with description and options
-d            | Only download the files, without decompressing (-o will be ignored, do not use with -u)
-u            | Only unpacks already downloaded files (use with -z, do not use with -d)
-z \<dir\>    | Expects a directory, in which the tars will be downloaded
-o \<dir\>    | Expects a directory, in which the radar files will be extracted to
-m            | Download files with the resolution of 5 minutes, instead of resolution of 1 hour
-y \<number\> | Specify a single year (instead of all years) to download or extract
