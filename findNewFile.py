import sqlite3
import logging
import sys
from os import scandir
from datetime import datetime

from sqlalchemy import create_engine

# CONSTANT VARIABLE
NETWORK_PATH = 'C:\\Stuff\\DevOp\\SearchFile\\filepath\\'


FILELIST_SQL = ''

DB_Config = {
    'DB_Type': 'sqlite',
    'DB_URL': 'fileList.db',
    'USER_NAME': '',
    'PASSWORD': '',
    'TABLE_NAME': ''
}

logging.basicConfig(filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
logging.info('This will get logged to a file')


def CreateConnection(connType, params):
    if connType == 'sqlite':
        return sqlite3.connect(params['DB_URL'])
    elif connType == 'mssql':
        return create_engine('mssql+pyodbc://USTRY1METV0496\TSASWATServer/TESTSWATDataAnalysis?driver=SQLServer?Username=DataTransferUser?Password=datatransferU$3r')
    else:
        pass
        # do something else


def GetFilesListFromDB():
    fileList = []
    try:
        connection = CreateConnection(DB_Config['DB_Type'], DB_Config)
        logging.info('Database connected successfully!')

        cursor = connection.cursor()
        cursor.execute('SELECT A, B, C FROM TABLE')
        for row in cursor:
            print('{},{},{}'.format(row.A, row.B, row.C))
            fileList.append(row.A)
        return fileList

    except sqlite3.DatabaseError as err:
        logging.error(err)
        sys.exit(1)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("DB connection is closed")


def convert_date(timestamp):
    d = datetime.utcfromtimestamp(timestamp)
    formatted_date = d.strftime('%d %b %Y')
    return formatted_date


def GetFilesListFromNetwork():
    fileListFromNet = []
    dir_entries = scandir(NETWORK_PATH)
    for entry in dir_entries:
        if entry.is_file():
            info = entry.stat()
            logging.info(
                f'{entry.name}\t Last Modified: {convert_date(info.st_mtime)}')
            print(f'{entry.name}\t Last Modified: {convert_date(info.st_mtime)}')
            fileListFromNet.append((entry.name, convert_date(info.st_mtime)))
    return set(fileListFromNet)


def FindNewFilelist():
    netFilesList = GetFilesListFromNetwork()
    dbFileList = GetFilesListFromDB()

    for i in netFilesList:
        if i.name in dbFileList:
            netFilesList.remove(i)
    return netFilesList


def UpdateDBWithNewFile():
    pass
