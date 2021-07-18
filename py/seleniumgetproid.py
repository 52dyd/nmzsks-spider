# 通过selenium驱动浏览器以便从懒加载网页中爬取信息
# 实现从每小时报考信息主页由院校代号获得专业代号
import copy
from selenium import webdriver
import time
import pymysql


def getlist(s, uni_id, uni_name):
    anslist = []
    tmplist = [uni_id, uni_name]
    while len(s) > 0:
        if s[0] == ' ':
            while s[0] == ' ':
                s = s[1:len(s)]
        elif s[0] == '\n':
            if(len(tmplist) > 3):
                anslist.append(copy.deepcopy(tmplist))
            tmplist = [uni_id, uni_name]
            s = s[1:len(s)]
        else:
            tmplist.append(s[0:s.find(' ')])
            s = s[s.find(' '):len(s)]
    return anslist

db = pymysql.connect(host='localhost', port=3306, user='root', password='52Dyd1314,.', database='gkbm2021')
cursor = db.cursor()
sql = 'select * from university'
cursor.execute(sql)
uni = cursor.fetchall()
driver_path = r'C:\Users\18365\Desktop\ksbm\msedgedriver.exe'  # 浏览器驱动
driver = webdriver.Edge(executable_path=driver_path)
url = r'https://www.nm.zsks.cn/21gkwb/gktj_21_31_20/tj/tjzy.html?path=3B294'
driver.get(url)
time.sleep(5) # 第一次加载会比较慢，等待时间稍长
for i in uni:
    url = r'https://www.nm.zsks.cn/21gkwb/gktj_21_31_20/tj/tjzy.html?path=3B' + i[0].upper()
    driver.get(url)
    time.sleep(0.25)  # 此处为同步等待，selenium可以实现异步加载，既当某个元素加载完成后直接爬取而并不等待整个页面加载完
    # 但是具体到改网页，需要爬取的信息在<table>中，但<table>标签一直存在，被懒加载的只是<table>中的内容，无法定位，故选择同步等待
    s = driver.find_element_by_id("table").text
    s += '\n'
    s = s.replace('\n', ' \n')
    s = getlist(s, i[0], i[1])

    sql = '''insert into li_uni
(id, name, proid, proname, getnum, minscr, cost, location, descrb)
values
('%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s');'''
    for j in s:

        value = (j[0], j[1], j[2], j[3], j[5], j[6], j[9], j[11], j[12])
        try:
            cursor.execute(sql % value)
            db.commit()
        except BaseException as e:
            print(e)
            db.rollback()
            print(sql%value)
            input()
    print(s[0][1] + 'complete!')
driver.close()
