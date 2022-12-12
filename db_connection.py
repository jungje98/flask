import pymysql


 # sql 연동

db = pymysql.connect(
    host = 'localhost',
    user = 'root',
    db = 'snack',
    password = '0516',
    charset='utf8'
)

cur = db.cursor()

sql = "SELECT * from core_snack"
cur.execute(sql)

data_list = cur.fetchall()

data_list