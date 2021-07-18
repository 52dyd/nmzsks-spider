import pymysql



db = pymysql.connect(host="localhost", port=3306, user='root', password='52Dyd1314,.')
cursor = db.cursor()
sql = 'use gkbm2021;'
try:
    cursor.execute(sql)
    db.commit()
except BaseException as e:
    db.rollback()
for i in ctt:
    sql = '''insert into university
    (id, name)
    values
    (\'''' + i['院校代号'] + '''\', \'''' + i['院校名称'] + '''\');'''
    try:
        cursor.execute(sql)
        db.commit()
    except BaseException as e:
        db.rollback()
db.close()
