import pymysql

db = pymysql.connect(host='localhost', port=3306, user='root', password='52Dyd1314,.', database='gkbm2021')
cursor = db.cursor()
sql = '''select * from wen_stu;'''
cursor.execute(sql)
stu = cursor.fetchall()
with open('wenstu.txt', 'w+') as f:
    for i in stu:
        #f.write(str(i[1:len(i) - 1]) + '\n')
        f.write(str(i[1:2])[2:6] + '*****' + str(i[1:2])[12:len(str(i[1:2]))-3]+'\n')
f.close()