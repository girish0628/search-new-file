from os import scandir
from datetime import datetime
import os
entries = os.listdir('C:\\Stuff\\DevOp\\SearchFile\\filepath\\')

filename = r'C:\Stuff\DevOp\SearchFile\filepath\check_folder.txt'

print(os.path.getsize(filename))
print(os.path.getmtime(filename))
print(os.path.getctime(filename))

print(os.stat(filename))

stats = os.stat(filename)

print(stats.st_size)
print(stats.st_mtime)

print(entries)
print("========================================")


def convert_date(timestamp):
    d = datetime.utcfromtimestamp(timestamp)
    formatted_date = d.strftime('%d %b %Y')
    return formatted_date


def get_files():
    dir_entries = scandir('C:\\Stuff\\DevOp\\SearchFile\\filepath\\')
    for entry in dir_entries:
        if entry.is_file():
            info = entry.stat()
            print(f'{entry.name}\t Last Modified: {convert_date(info.st_mtime)}')


get_files()
