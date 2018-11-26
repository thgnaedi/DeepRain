import tarfile
import gzip
import glob, os, shutil


def gunzip(file_path, output_path):
    with gzip.open(file_path, "rb") as comressed, open(output_path, "wb") as file_out:
        shutil.copyfileobj(comressed, file_out)

def uncompress_houly(folder_path):
    os.chdir(folder_path)
    for file in glob.glob("*bin.gz"):
        with gzip.open(file, "rb") as hourly_compressed:
            a = "A"
            # ToDo


def uncompress_monthly(tar_file_path, destination):
    file = tarfile.open(tar_file_path, "r:gz")
    file.extractall(destination)


def main():
    for file in glob.glob("*.tar.gz"):
        uncompress_monthly(file, ".")


if __name__ == "__main__":
    main()
