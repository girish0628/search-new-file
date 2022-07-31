import sys, time, copy
from os import walk, path, stat
from datetime import datetime
import pyodbc

# CONSTANT VARIABLE
NETWORK_PATH = "C:\\Stuff\\DevOp\\SyncFolder\\root\\B020_DG-0334"


FILELIST_SQL = "SELECT * FROM B020DG0334"
FILE_INSERT_SQL = "INSERT INTO B020DG0334 (FileName, FileSizeInByte, DateRecieved, IsDeleted, SentFrom) VALUES (?, ?, ?, ?, ?)"


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
        print("Database connected successfully!")

        cursor = connection.cursor()
        cursor.execute(FILELIST_SQL)
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
        print(err)
        sys.exit(1)
    finally:
        cursor.close()
        connection.close()
        print("DB connection is closed")


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

    cursor.executemany(FILE_INSERT_SQL, params)
    connection.commit()
    cursor.close()
    connection.close()


###### _Start
FindNewFilelist()
