# import pyodbc

# conn = pyodbc.connect(
#     "Driver={SQL Server};"
#     "Server=DESKTOP-04M1VG7\SQLEXPRESS;"
#     "Database=dev_g;"
#     "Trusted_Connection=yes;"
# )

# cursor = conn.cursor()
# cursor.execute("SELECT * FROM B020DG0334")

# for i in cursor:
#     print(i)

import os
from os import listdir
from os.path import isfile, join

import time

NETWORK_PATH = "C:\\Stuff\\DevOp\\SyncFolder\\root\\B020_DG-0334"

# Getting the current work directory (cwd)
thisdir = os.getcwd()

# r=root, d=directories, f = files
for r, d, f in os.walk(NETWORK_PATH):
    for file in f:
        print(r, file, os.path.join(r, file))
        # print(os.stat(os.path.join(r, file)))
        # fileStatsObj = os.stat(os.path.join(r, file))
        # modificationTime = time.ctime(fileStatsObj[os.stat.ST_MTIME])
        # print("Last Modified Time : ", modificationTime)

        # Get file's Last modification time stamp only in terms of seconds since epoch
        modTimesinceEpoc = os.path.getmtime(os.path.join(r, file))
        # Convert seconds since epoch to readable timestamp
        modificationTime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(modTimesinceEpoc)
        )
        print("Last Modified Time : ", modificationTime)


import logging
import sys, time, copy
from os import walk, path, stat
from datetime import datetime
import pyodbc

# CONSTANT VARIABLE
NETWORK_PATH = "C:\\Stuff\\DevOp\\SyncFolder\\root\\B020_DG-0334"


FILELIST_SQL = ""


logging.basicConfig(
    filename="app.log", filemode="w", format="%(name)s - %(levelname)s - %(message)s"
)
logging.info("This will get logged to a file")


def CreateConnection():
    return pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-04M1VG7\SQLEXPRESS;"
        "Database=dev_g;"
        "Trusted_Connection=yes;"
    )


def GetFilesListFromDB():
    fileList = []
    try:
        connection = CreateConnection()
        logging.info("Database connected successfully!")

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM B020DG0334")
        for row in cursor:
            # print(
            #     "{},{},{},{},{},{}".format(
            #         row.TransmissionID,
            #         row.FileName,
            #         row.FileSizeInByte,
            #         row.DateRecieved,
            #         row.IsDeleted,
            #         row.SentFrom,
            #     )
            # )
            fileList.append(row.FileName)
        return fileList, connection

    except pyodbc.Error as err:
        logging.error(err)
        sys.exit(1)
    finally:
        cursor.close()
        connection.close()
        logging.info("DB connection is closed")


def convert_date(timestamp):
    d = datetime.utcfromtimestamp(timestamp)
    formatted_date = d.strftime("%d %b %Y")
    return formatted_date


def getDateFromPath(fileName, file_path):
    # Get file's Last modification time stamp only in terms of seconds since epoch
    modified = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(path.getmtime(file_path))
    )
    created = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(path.getctime(file_path))
    )
    filesize = stat(file_path).st_size
    # return created, modified
    return fileName, filesize, created, 0, file_path


def GetFilesListFromNetworkOld():
    fileListFromNet = []
    dir_entries = scandir(NETWORK_PATH)
    for entry in dir_entries:
        if entry.is_file():
            info = entry.stat()
            logging.info(f"{entry.name}\t Last Modified: {convert_date(info.st_mtime)}")
            print(f"{entry.name}\t Last Modified: {convert_date(info.st_mtime)}")
            fileListFromNet.append((entry.name, convert_date(info.st_mtime)))
    return set(fileListFromNet)


def GetFilesListFromNetwork():
    fileListFromNet = []
    # r=root, d=directories, f = files
    for r, d, f in walk(NETWORK_PATH):
        for file in f:
            file_path = path.join(r, file)
            # print(f"{file}\t Last Modified: {getDateFromPath(file_path)}")
            fileListFromNet.append(getDateFromPath(file, file_path))
    return set(fileListFromNet)


def FindNewFilelist():
    netFilesList = GetFilesListFromNetwork()
    dbFileList, connection = GetFilesListFromDB()
    print(netFilesList)
    print(dbFileList)

    # for i in netFilesList:
    #     print(i[0])

    for i in copy.copy(netFilesList):
        if i[0] in dbFileList:
            netFilesList.remove(i)

    UpdateDBWithNewFile(connection, netFilesList)
    print("Sync process completed..!")
    # return netFilesList


def UpdateDBWithNewFile(connection, params):
    # connection = CreateConnection()
    cursor = connection.cursor()
    cursor.fast_executemany = True
    # params = [
    #     (
    #         "b21.txt",
    #         28644,
    #         "2022-07-31 19:03:53",
    #         0,
    #         "C:\\Stuff\\DevOp\\SyncFolder\\root\\B020_DG-0334\\b20\\b21.txt",
    #     ),
    #     (
    #         "test.txt",
    #         0,
    #         "2022-07-31 19:03:45",
    #         0,
    #         "C:\\Stuff\\DevOp\\SyncFolder\\root\\B020_DG-0334\\test.txt",
    #     ),
    # ]

    SQL = "INSERT INTO B020DG0334 (FileName, FileSizeInByte, DateRecieved, IsDeleted, SentFrom) VALUES (?, ?, ?, ?, ?)"

    cursor.executemany(SQL, params)
    connection.commit()
    cursor.close()
    connection.close()


# print(GetFilesListFromDB())
# print(GetFilesListFromNetwork())
# print(list(FindNewFilelist()))
