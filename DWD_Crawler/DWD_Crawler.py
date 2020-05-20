import argparse
import os.path
from ftplib import FTP
import glob
import gzip
import shutil
import tarfile
import os
import requests
import logging
import uuid


logger = logging.getLogger("DWD Crawler (script)")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("dwd-crawler.log")
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


FTP_DIRECTORY = "/climate_environment/CDC/grids_germany/{}/radolan/historical/bin/"
host_protocol = "ftp://"
host_url = "ftp-cdc.dwd.de"
#host_url = "ftp://opendata.dwd.de"
#host_directory = "pub/CDC/grids_germany/hourly/radolan/historical/bin/"
#host_directory = "/climate_environment/CDC/grids_germany/hourly/radolan/historical/bin/"
host_directory = FTP_DIRECTORY.format("hourly")
local_directory = "./"

minutely_host_protocol = "https://"
#minutely_host_url = "opendata.dwd.de/climate_environment/CDC/grids_germany/5_minutes/radolan/reproc/2017_002/bin/"
minutely_host_url = FTP_DIRECTORY[1:].format("5_minutes")
minutely_year_begin = 2001
minutely_year_end = 2018
minutely_filename_prefix = "YW2017.002_"
minutely_filename_end = ".tar"


def daily_uncompress(archive_directory, target_directory, year=None):
    temp_dir_name = "tmp_" + str(uuid.uuid4())
    os.chdir(archive_directory)
    if not os.path.isdir(temp_dir_name):
        os.mkdir(temp_dir_name)

    if not year:
        archive_wildcard = minutely_filename_prefix + "*.tar"
    else:
        archive_wildcard = minutely_filename_prefix + str(year) + "*.tar"

    for file in glob.glob(archive_wildcard):
        uncompress_tarfile(archive_directory + '/' + file, "./" + temp_dir_name)

    # Move to tmp directory and uncompress archives to target
    os.chdir(temp_dir_name)
    logger.info("Uncompressing .tar.gz files in " + os.getcwd())
    for file in glob.glob("*.tar.gz"):
        uncompress_targzfile(file, target_directory)
    logger.info("Removing temp folder")
    os.chdir("..")
    shutil.rmtree("./" + temp_dir_name)


def daily_download_years(target_directory):
    for year in range(minutely_year_begin, minutely_year_end + 1):
        daily_download_months(year, target_directory)


def daily_download_months(year, target_directory):
    for month in range(1, 13):
        daily_filename = minutely_filename_prefix + str(year) + str(month).zfill(2) + minutely_filename_end
        url_complete = minutely_host_protocol + minutely_host_url + str(year) + '/' + daily_filename
        if os.path.isfile(target_directory + daily_filename):
            logger.info("File already downloaded: " + daily_filename)
            continue
        logger.info("Downloading: " + url_complete)
        r = requests.get(url_complete, stream=True)
        r.raw.decode_content = True
        with open(target_directory + daily_filename, 'wb') as file:
            file.write(r.content)


def gunzip(file_path, output_path):
    logger.info("Uncompressing gz file: " + file_path)
    with gzip.open(file_path, "rb") as compressed, open(output_path, "wb") as file_out:
        shutil.copyfileobj(compressed, file_out)


def uncompress_tarfile(tar_file_path, destination):
    if tarfile.is_tarfile(tar_file_path):
        logger.info("Uncompressing tar file: " + tar_file_path)
        file = tarfile.open(tar_file_path, "r|")
        file.extractall(destination)
    else:
        logger.error("Error uncompressing tar file: " + tar_file_path)


def uncompress_targzfile(tar_file_path, destination):
    if tarfile.is_tarfile(tar_file_path):
        logger.info("Uncompressing tar.gz file: " + tar_file_path)
        file = tarfile.open(tar_file_path, "r:gz")
        try:
            file.extractall(destination)
        except:
            logger.error("Extraction failed for: {}".format(tar_file_path))
    else:
        logger.error("Error uncompressing tar.gz file: " + tar_file_path)


def uncompress_monthly_all(source_path, destination_path):
    os.chdir(source_path)
    for file in glob.glob("*.tar.gz"):
        subdir = os.path.join(destination_path, file[:-7])  #-7 = folder without .tar.gz!
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        uncompress_targzfile(file, subdir)


def download_with_new_connection(ftp, filename):
    if os.path.isfile(filename):
        logger.info("File " + filename + " already downloaded!")
    else:
        logger.info("Downloading: " + ftp.pwd() + filename)
        with open(filename, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)


def download_files(ftp, file_list):
    for file in file_list:
        if file[0]:
            download_with_new_connection(ftp, file[1])


def ftp_file(ftp, directory):
    dir_listing = []
    ftp.cwd(directory)
    ftp.dir(lambda x: dir_listing.append(x))
    return [(line[0].upper() != 'D', line.rsplit()[-1]) for line in dir_listing]


def ftp_dir(ftp, directory):
    dir_listing = []
    ftp.cwd(directory)
    ftp.dir(lambda x: dir_listing.append(x))
    return [(line[0].upper() == 'D', line.rsplit()[-1]) for line in dir_listing]


def ftp_dir_year(ftp, directory_file_list):
    for df in directory_file_list:
        if df[0]:
            current_directory = df[1]
            file_list = ftp_file(ftp, current_directory)
            download_files(ftp, file_list)
            ftp.cwd("..")


def main(download_dir="./", out_directory="./", download=True, unpack=True, minutely=True, year=None):
    logger.info("Downloads are at: " + download_dir)
    logger.info("Uncompressing to: " + out_directory)

    logger.info("Doing: ")

    #ToDo: year selection currently only used with minutely = True
    #ToDo: minutely Download has to be fixed
    #ToDo: Error handling for ftp/http connections

    if download:
        if not minutely:
            logger.info("Downloading hourly files")
            os.chdir(download_dir)
            ftp_session = FTP(host_url)
            ftp_session.login()
            ftp_dir_year(ftp_session, ftp_dir(ftp_session, host_directory))
            ftp_session.close()
        else:
            logger.info("Downloading minutely files")
            if not year:
                daily_download_years(download_dir)
            else:
                num_year = int(year)
                if minutely_year_begin <= num_year <= minutely_year_end:
                    daily_download_months(num_year, download_dir)
                else:
                    logger.info("Year not available for download: " + str(year))

    if unpack:
        if not minutely:
            print("Uncompressing hourly files")
            uncompress_monthly_all(download_dir, out_directory)
        else:
            print("Uncompressing minutely files")
            daily_uncompress(download_dir, out_directory, year)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads and extracts radio data from DWD ftp server")
    parser.add_argument("-z", "--downloadDir",
                        dest="down_directory",
                        help="Target directory for downloads.")
    parser.add_argument("-o", "--outputDir",
                        dest="out_directory",
                        help="Target directory for binary files.")
    parser.add_argument("-d", "--download-only",
                        dest="downloadOnly",
                        help="Download only, do not unpack.",
                        action="store_true")
    parser.add_argument("-u", "--unpack-only",
                        dest="unpackOnly",
                        help="Only unpack, do not download.",
                        action="store_true")
    parser.add_argument("-m", "--minutely",
                        dest="minutely",
                        help="Download files containing data for every 5 minutes, instead of hourly data",
                        action="store_true")
    parser.add_argument("-y", "--year",
                        dest="year",
                        help="Specify the year to be downloaded. ONLY WORKS with option: -m")

    logger.info("All Arguments initialized")

    args = parser.parse_args()
    logger.info("Parsed arguments:")
    logger.info("downloadOnly: ")
    logger.info("True" if args.downloadOnly else "False")
    logger.info("unpackOnly: ")
    logger.info("True" if args.unpackOnly else "False")
    logger.info("hourly files: ")
    logger.info("True" if not args.minutely else "False")
    logger.info("5 minutely files: ")
    logger.info("True" if args.minutely else "False")

    logger.info("Download YEAR: " + ("ALL" if not args.year else str(args.year)))

    down_dir = "./" if args.down_directory is None else os.path.join(args.down_directory, '')
    out_dir = "./" if args.out_directory is None else os.path.join(args.out_directory, '')

    if args.downloadOnly and args.unpackOnly:
        logger.error("Contradicting arguments: downloadOnly AND unpackOnly")
        logger.info("YOU wanted me to do nothing!!!")
        logger.info("Exiting now - tschau!")
    else:
        main(download_dir=down_dir,
             out_directory=out_dir,
             download=not args.unpackOnly,
             unpack=not args.downloadOnly,
             minutely=args.minutely,
             year=args.year)
    logger.info("Crawler finished!")
