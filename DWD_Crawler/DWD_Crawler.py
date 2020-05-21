import argparse
import os.path
from ftplib import FTP
import glob
import gzip
import shutil
import tarfile
import os
import logging


logger = logging.getLogger("DWD Crawler (script)")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("dwd-crawler.log")
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

host_url = "ftp-cdc.dwd.de"
host_directory = "/climate_environment/CDC/grids_germany/hourly/radolan/historical/bin/"

minutely_host_url = "/climate_environment/CDC/grids_germany/5_minutes/radolan/reproc/2017_002/bin/"
minutely_year_begin = 2001
minutely_year_end = 2019

def gunzip(file_path, output_path):
    logger.info("Uncompressing gz file: " + file_path)
    with gzip.open(file_path, "rb") as compressed, open(output_path, "wb") as file_out:
        shutil.copyfileobj(compressed, file_out)



def uncompress_targzfile(tar_file_path, destination, method="r:gz"):
    """
    Extracting archive File to destination
    :param tar_file_path:   path to archive File (.tar, .tar.gz, ...)
    :param destination:     directory to extract archive
    :param method:          r:gz for .tar.gz r for tar etc, modes can be found in tarfile.open description
    :return:
    """
    if tarfile.is_tarfile(tar_file_path):
        logger.info("Uncompressing tar.gz file: " + tar_file_path)
        file = tarfile.open(tar_file_path, method)
        try:
            file.extractall(destination)
        except:
            logger.error("Extraction failed for: {}".format(tar_file_path))
    else:
        logger.error("Error uncompressing tar.gz file: " + tar_file_path)


def uncompress_all(source_path, destination_path, archiveFormat = "*.tar.gz"):
    os.chdir(source_path)
    for file in glob.glob(archiveFormat):
        subdir = os.path.join(destination_path, file[:-(len(archiveFormat)-1)])  #-7 = folder without .tar.gz!
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        if archiveFormat.endswith(".gz"):   #*.tar.gz
            uncompress_targzfile(file, subdir)
        elif archiveFormat.endswith(".tar"):    #*.tar
            uncompress_targzfile(file, subdir, "r|")
        else:
            logger.error("unsupported format for uncompress_all found, nothing to do here!")
    return


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


def ftp_dir_year(ftp, directory_file_list, year=None):
    for df in directory_file_list:
        if year is not None:
            if df[1] != year:   # skipping unnecessary years
                continue
        if df[0]:
            current_directory = df[1]
            file_list = ftp_file(ftp, current_directory)
            download_files(ftp, file_list)
            ftp.cwd("..")


def main(download_dir="./", out_directory="./", download=True, unpack=True, minutely=True, year=None):
    logger.info("Downloads are at: " + download_dir)
    logger.info("Uncompressing to: " + out_directory)
    logger.info("Doing: ")


    if download:
        if not minutely:
            logger.info("Downloading hourly files")
            os.chdir(download_dir)
            try:
                ftp_session = FTP(host_url)
                ftp_session.login()
            except Exception as e:
                logger.error("FTP Session for {} failed. \nException:{}".format(host_url,e))
                return
            ftp_dir_year(ftp_session, ftp_dir(ftp_session, host_directory), year)
            ftp_session.close()
        else:
            logger.info("Downloading minutely files")
            os.chdir(download_dir)
            try:
                ftp_session = FTP(host_url)
                ftp_session.login()
            except Exception as e:
                logger.error("FTP Session for {} failed. \nException:{}".format(host_url, e))
                return
            ftp_dir_year(ftp_session, ftp_dir(ftp_session, minutely_host_url), year)
            ftp_session.close()

    if unpack:
        if not minutely:
            print("Uncompressing hourly files")
            uncompress_all(download_dir, out_directory)
        else:
            print("Uncompressing minutely files")
            uncompress_all(download_dir, out_directory, archiveFormat="*.tar")

    logger.info("Crawler finished!")


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
                        help="Specify the year to be downloaded.")

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
        logger.info("youse only one of them, or noone to download and extract")
    else:
        main(download_dir=down_dir,
             out_directory=out_dir,
             download=not args.unpackOnly,
             unpack=not args.downloadOnly,
             minutely=args.minutely,
             year=args.year)

