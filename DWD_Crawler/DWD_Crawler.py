import argparse
import os.path
from ftplib import FTP
import glob
import gzip
import shutil
import tarfile
import os

host_protocol = "ftp://"
host_url = "ftp-cdc.dwd.de"
host_directory = "pub/CDC/grids_germany/hourly/radolan/historical/bin/"
local_directory = "./"


def gunzip(file_path, output_path):
    with gzip.open(file_path, "rb") as compressed, open(output_path, "wb") as file_out:
        shutil.copyfileobj(compressed, file_out)


def uncompress_monthly(tar_file_path, destination):
    file = tarfile.open(tar_file_path, "r:gz")
    file.extractall(destination)


def uncompress_monthly_all(source_path, destination_path):
    os.chdir(source_path)
    for file in glob.glob("*.tar.gz"):
        subdir = destination_path + '/' + file
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        uncompress_monthly(file, subdir)


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


def main(download_dir="./", out_directory="./", download=True, unpack=True):
    print("Hello From Main!!!")
    print("Downloading to: " + download_dir)
    print("Unzipping to: " + out_directory)
    if download:
        os.chdir(download_dir)
        ftp_session = FTP(host_url)
        ftp_session.login()
        ftp_dir_year(ftp_session, ftp_dir(ftp_session, host_directory))
        ftp_session.close()

    if unpack:
        uncompress_monthly_all(download_dir, out_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads and extracts radio data from DWD ftp server")
    parser.add_argument("-z", "--downloadDir",   dest="down_directory", help="Target directory for downloads.")
    parser.add_argument("-o", "--outputDir",     dest="out_directory", help="Target directory for binary files.")
    parser.add_argument("-d", "--download-only", dest="downloadOnly",  help="Download only, do not unpack.", action="store_true")
    parser.add_argument("-u", "--unpack-only",   dest="unpackOnly",    help="Only unpack, do not download.", action="store_true")
    print("All Arguments initialized")

    args = parser.parse_args()
    print("Parsed arguments:")
    print("down_directory: " + "None" if args.down_directory is None else args.down_directory)
    print("out_directory: "  + "None" if args.out_directory is None else args.out_directory)
    print("downloadOnly: "   + "True" if args.downloadOnly else "False")
    print("unpackOnly: "     + "True" if args.unpackOnly else "False")

    down_dir = "./" if args.down_directory is None else args.down_directory
    out_dir = "./" if args.out_directory is None else args.out_directory

    if args.downloadOnly and args.unpackOnly:
        print("Arguments contradict each other!!! downloadOnly && unpackOnly")
    elif args.downloadOnly:
        main(download_dir=down_dir, out_directory=out_dir, download=True, unpack=False)
    elif args.unpackOnly:
        main(download_dir=down_dir, out_directory=out_dir, download=False, unpack=True)
    else:
        main(download_dir=down_dir, out_directory=out_dir, download=True, unpack=True)
    print("Returned from main()")
