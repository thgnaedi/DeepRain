from ftplib import FTP

host_protocol = "ftp://"
host_url = "ftp-cdc.dwd.de"
host_directory = "pub/CDC/grids_germany/hourly/radolan/historical/bin/"
local_directory = "./"


def download_with_new_connection(ftp, filename):
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


def main():
    ftp_session = FTP(host_url)
    ftp_session.login()

    ftp_dir_year(ftp_session, ftp_dir(ftp_session, host_directory))

    ftp_session.close()


if __name__ == "__main__":
    main()
