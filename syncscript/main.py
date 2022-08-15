import sys, time, copy
from os import walk, path, stat
from datetime import datetime
import pyodbc

# CONSTANT VARIABLE
# NETWORK_PATH = r"C:\Stuff\DevOp\SyncFolder\search-new-file\root\B020_DG-0334"

FILE_PATH_LIST_SQL = "SELECT * FROM ProjectShareLookup"
FILELIST_SQL = "SELECT * FROM DataTransmissionLog"
FILE_INSERT_SQL = "INSERT INTO DataTransmissionLog (Filename, FileSizeInBytes, DataReceived, IsDeleted, SentFrom) VALUES (?, ?, ?, ?, ?)"


def CreateConnection(dbName):
    return pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-04M1VG7\SQLEXPRESS;"
        "Database=" + dbName + ";"
        "Trusted_Connection=yes;"
    )


def GetFilesListFromDB():
    fileList = []
    try:
        connection = CreateConnection("dev_g")
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
        return fileList

    except pyodbc.Error as err:
        print(err)
        sys.exit(1)
    finally:
        cursor.close()
        connection.close()
        print("DB connection is closed")


def GetNetworkPathFromDB():
    rootFileList = []
    try:
        connection = CreateConnection("SWATDataAnalysis")
        print("Database connected successfully!")

        cursor = connection.cursor()
        cursor.execute(FILE_PATH_LIST_SQL)

        for row in cursor:
            fileShr = row.FileShare.lower()
            rootFolder = row.FileShare.split("\\")[-1]
            if row.DriveID == 7:
                rootFileList.append(("j:/SWATTransmissions/{}".format(rootFolder), row.id))
                # rootFileList.append(fileShr.replace(r"\\ustry1metv0496", "j:\\"))
            if row.DriveID == 5:
                # rootFileList.append(fileShr.replace(r"\\ustry1metv0496", "g:\\"))
                rootFileList.append(("g:/SWATTransmissions/{}".format(rootFolder), row.id))
        return rootFileList

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
    netFilesLists = GetNetworkPathFromDB()
    for NETWORK_PATH, id in netFilesLists:
        for r, d, f in walk(NETWORK_PATH):
            for file in f:
                file_path = path.join(r, file)
                # print(f"{file}\t Last Modified: {getDateFromPath(file_path)}")
                fileListFromNet.append((getDateFromPath(file, file_path), id))
    return set(fileListFromNet)


def FindNewFilelist():
    dbFileList = GetFilesListFromDB()
    netFilesList = GetFilesListFromNetwork()
    for i in copy.copy(netFilesList):
        if i[0] in dbFileList:
            netFilesList.remove(i)

    UpdateDBWithNewFile(netFilesList)
    print("Sync process completed..!")
    # return netFilesList


def UpdateDBWithNewFile(params):
    connection = CreateConnection()
    cursor = connection.cursor()
    cursor.fast_executemany = True
    print(params)
    cursor.executemany(FILE_INSERT_SQL, list(params))
    connection.commit()
    cursor.close()
    connection.close()


###### _Start
# FindNewFilelist()
print(GetFilesListFromNetwork())
