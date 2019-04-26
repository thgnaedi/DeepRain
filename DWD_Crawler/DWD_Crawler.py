import argparse
import os.path
from ftplib import FTP
import glob
import gzip
import shutil
import tarfile
import os
import requests

host_protocol = "ftp://"
host_url = "ftp-cdc.dwd.de"
host_directory = "pub/CDC/grids_germany/hourly/radolan/historical/bin/"
local_directory = "./"

minutely_host_protocol = "https://"
minutely_host_url = "opendata.dwd.de/climate_environment/CDC/grids_germany/5_minutes/radolan/reproc/2017_002/bin/"
minutely_range_begin = 2001
minutely_range_end = 2018
minutely_filename_prefix = "YW2017.002_"
minutely_filename_end = ".tar"


def daily_uncompress(archive_directory, target_directory):
    temp_dir_name = "tmp"
    os.chdir(archive_directory)
    if not os.path.isdir(temp_dir_name):
        os.mkdir(temp_dir_name)
    for file in glob.glob("*.tar"):
        uncompress_tarfile(archive_directory + '/' + file, "./" + temp_dir_name)

    # Move to tmp directory and uncompress archives to target
    os.chdir(temp_dir_name)
    print("Uncompressing .tar.gz files in " + os.getcwd())
    for file in glob.glob("*.tar.gz"):
        uncompress_targzfile(file, target_directory)


def daily_download_years(target_directory):
    for year in range(minutely_range_begin, minutely_range_end):
        daily_download_months(year, target_directory)


def daily_download_months(year, target_directory):
    for month in range(1, 12):
        daily_filename = minutely_filename_prefix + str(year) + str(month).zfill(2) + minutely_filename_end
        url_complete = minutely_host_protocol + minutely_host_url + str(year) + '/' + daily_filename
        if os.path.isfile(target_directory + daily_filename):
            print("File already downloaded: " + daily_filename)
            continue
        print("Downloading: " + url_complete)
        r = requests.get(url_complete, verify=False, stream=True)
        r.raw.decode_content = True
        with open(target_directory + daily_filename, 'wb') as file:
            shutil.copyfileobj(r.raw, file)


def gunzip(file_path, output_path):
    print("Uncompressing gz file: " + file_path)
    with gzip.open(file_path, "rb") as compressed, open(output_path, "wb") as file_out:
        shutil.copyfileobj(compressed, file_out)


def uncompress_tarfile(tar_file_path, destination):
    print("Uncompressing tar file: " + tar_file_path)
    file = tarfile.open(tar_file_path, "r|")
    file.extractall(destination)


def uncompress_targzfile(tar_file_path, destination):
    print("Uncompressing tar.gz file: " + tar_file_path)
    file = tarfile.open(tar_file_path, "r:gz")
    file.extractall(destination)


def uncompress_monthly_all(source_path, destination_path):
    os.chdir(source_path)
    for file in glob.glob("*.tar.gz"):
        subdir = destination_path + '/' + file
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        uncompress_targzfile(file, subdir)


def download_with_new_connection(ftp, filename):
    if os.path.isfile(filename):
        print("File " + filename + " already downloaded!")
    else:
        print("Downloading: " + ftp.pwd() + filename)
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


def main(download_dir="./", out_directory="./", download=True, unpack=True, minutely=True):
    print("Downloads are at: " + download_dir)
    print("Uncompressing to: " + out_directory)

    print("Doing: ")

    if download:
        if not minutely:
            print("Downloading hourly files")
            os.chdir(download_dir)
            ftp_session = FTP(host_url)
            ftp_session.login()
            ftp_dir_year(ftp_session, ftp_dir(ftp_session, host_directory))
            ftp_session.close()
        else:
            print("Downloading minutely files")
            daily_download_years(download_dir)

    if unpack:
        if not minutely:
            print("Uncompressing hourly files")
            uncompress_monthly_all(download_dir, out_directory)
        else:
            print("Uncompressing minutely files")
            daily_uncompress(download_dir, out_directory)


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

    print("All Arguments initialized")

    args = parser.parse_args()
    print("Parsed arguments:")
    print("downloadOnly: ", end='', flush=True)
    print("True" if args.downloadOnly else "False")
    print("unpackOnly: ", end='', flush=True)
    print("True" if args.unpackOnly else "False")
    print("hourly files: ", end='', flush=True)
    print("True" if not args.minutely else "False")
    print("5 minutely files: ", end='', flush=True)
    print("True" if args.minutely else "False")

    down_dir = "./" if args.down_directory is None else args.down_directory
    out_dir = "./" if args.out_directory is None else args.out_directory

    if args.downloadOnly and args.unpackOnly:
        print("Arguments contradict each other!!! downloadOnly && unpackOnly")
    else:
        main(download_dir=down_dir,
             out_directory=out_dir,
             download=not args.unpackOnly,
             unpack=not args.downloadOnly,
             minutely=args.minutely)
    print("Crawler finished!")
