import MySQLdb

##pip install MySQLdb
##sudo apt-get install python-mysqldb
def connection():
    connec= MySQLdb.connect(host="localhost",
                            user="root",
                            passwd="",
                            db="pageDB" )
    c = connec.cursor()
    return c, connec
