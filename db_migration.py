import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# CONSTANT VARIABLE
NETWORK_PATH = 'C:\\Stuff\\DevOp\\SearchFile\\filepath\\'

FILELIST_SQL = ''

DB_Config = {
    'DB_Type': 'sqlite',
    'USER_NAME': 'DataTransferUser',
    'PASSWORD': 'datatransferU$3r',
    'TABLE_NAME': 'TESTSWATDataAnalysis'
}

SQL_QUERIES = {
    'SQL1': 'SELECT * FROM table_name',
    'SQL2': 'SELECT * FROM table_name',
    'SQL3': 'SELECT * FROM table_name'
}

logging.basicConfig(filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
logging.info('This will get logged to a file')


def createConnection():
    db_url = 'mssql+pyodbc://USTRY1METV0496\TSASWATServer/{0}?driver=SQLServer?Username={1}?Password={2}'.format(
        DB_Config["TABLE_NAME"], DB_Config["USER_NAME"], DB_Config["PASSWORD"])
    return create_engine(db_url)


def executeSql():
    try:
        # Create connection
        conn = createConnection()
        for sql in SQL_QUERIES:
            logging.info(sql)
            row_count = conn.execute(sql)
            logging.info("Rows Added  = ", row_count.rowcount)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        logging.info(error)


def main():
    print("Process Started!")
    logging.info("Process Started!")
    executeSql()
    print("Process End!")
    logging.info("Process End!")


if __name__ == "__main__":
    main()
