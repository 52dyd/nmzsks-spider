import requests
import json
import pymysql
import time
from requests.packages import urllib3
import copy
import threading


class TableInfo:
    html_str = ''

    def __init__(self, htmlstr='', startloc=''):
        self.html_str = htmlstr.lower()
        self.html_str = self.html_str.replace('\n', '')
        self.html_str = self.html_str.replace('\r', '')
        self.html_str = self.html_str.replace(' ', '')
        self.html_str = self.html_str.replace(r'<br>', '')
        self.html_str = self.html_str.replace(r'&nbsp;', ' ')
        if startloc != '' and self.html_str.find(startloc) != -1:
            self.html_str = self.html_str[self.html_str.find(startloc) + 7: len(self.html_str)]
        return

    def setnxt(self):
        status = self.getnxt()
        if status == 0:
            self.html_str = self.html_str[self.html_str.find(r'<'): len(self.html_str)]
        else:
            self.html_str = self.html_str[self.html_str.find(r'>') + 1: len(self.html_str)]
        return

    def getnxt(self):
        while True:
            if self.html_str[0] != r'<':
                return 0
            else:
                if self.html_str[0:6] == r'<table':
                    return 1
                elif self.html_str[0:3] == r'<tr':
                    return 2
                elif self.html_str[0:3] == r'<td':
                    return 3
                elif self.html_str[0:3] == r'<th':
                    return 3
                elif self.html_str[0:4] == r'</td':
                    return 4
                elif self.html_str[0:4] == r'</th':
                    return 4
                elif self.html_str[0:4] == r'</tr':
                    return 5
                elif self.html_str[0:7] == r'</table':
                    return 6
                elif self.html_str[0:] == r'</html>':
                    return 8
                else:
                    self.html_str = self.html_str[self.html_str.find('>') + 1: len(self.html_str)]

    def getline(self):
        tmplist = []
        status = self.getnxt()
        while status != 5:
            if status == 0:
                tmplist.append(self.html_str[0: self.html_str.find(r'<')])
            if status == 6:
                return []
            self.setnxt()
            status = self.getnxt()
        self.setnxt()
        return tmplist

    def gettable(self):
        anslist = []
        tmpdict = {}
        tmplist = []

        headlist = self.getline()
        status = self.getnxt()
        while status != 2:
            self.setnxt()
            status = self.getnxt()

        while status != 6:
            if status == 2:
                tmplist.clear()
                tmpdict.clear()
                tmplist = self.getline()
                for iii in range(0, len(tmplist)):
                    tmpdict[headlist[iii]] = tmplist[iii]
                anslist.append(copy.deepcopy(tmpdict))
            else:
                self.setnxt()
            status = self.getnxt()

        self.setnxt()
        return anslist

    def getgradetable(self):
        anslist = []

        tmplist = self.getline()
        status = self.getnxt()
        while status != 2:
            self.setnxt()
            status = self.getnxt()

        while status != 6:
            if status == 2:
                tmplist.clear()
                tmplist = self.getline()
                for iiii in range(0, len(tmplist), 3):
                    anslist.append(copy.deepcopy(tmplist[iiii:iiii+3]))
            else:
                self.setnxt()
            status = self.getnxt()

        self.setnxt()
        return anslist

    def getinfo(self):
        ansinfo = {}
        tmplist = []
        tmpstr = ''
        status = self.getnxt()
        while status != 8:
            if status == 0:
                tmpstr = self.html_str[0: self.html_str.find(r'<')]
                self.setnxt()
                if '考生考试情况' in tmpstr:
                    while status != 1:
                        status = self.getnxt()
                        self.setnxt()
                    tmplist.clear()
                    tmplist = self.getgradetable()
                    ansinfo[tmpstr] = copy.deepcopy(tmplist)
            else:
                while status != 1:
                    self.setnxt()
                    status = self.getnxt()
                tmplist.clear()
                tmplist = self.gettable()
                ansinfo[tmpstr] = copy.deepcopy(tmplist)
            status = self.getnxt()
        self.setnxt()
        return ansinfo


def getnum(s=''):   # 从某院校某专业中获取考生链接，形式为href:***.jsp?ksh=2115**********
    anslist = []
    status = s.find('jsp?')
    while status != -1:
        s = s[status + 4:len(s)]
        anslist.append(s[0:s.find('\'>')])
        status = s.find('jsp?')
    return anslist


def dicttosql(dict={}):  # 将取得的考生信息转换为sql语句
    sqlstr = '''('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')'''
    anstuple = (dict['考生基本情况：'][0]['考生号'], dict['考生基本情况：'][0]['性别'], dict['考生基本情况：'][0]['院校名称'][0:3],
                dict['考生基本情况：'][0]['院校名称'][3:len(dict['考生基本情况：'][0]['院校名称'])],
                dict['考生录取情况：'][0]['录取专业'][0:2],
                dict['考生录取情况：'][0]['录取专业'][2:len(dict['考生录取情况：'][0]['录取专业'])],
                dict['考生基本情况：'][0]['总分'], dict['考生基本情况：'][0]['特征分'],
                dict['考生考试情况：'][0][2], dict['考生考试情况：'][1][2], dict['考生考试情况：'][3][2],
                dict['考生考试情况：'][2][2], json.dumps(dict, ensure_ascii=False))
    return sqlstr % anstuple


def sqladd(s=''):  # 执行sql insert
    db = pymysql.connect(host='localhost', port=3306, user='root', password='52Dyd1314,.', database='gkbm2021')
    cursor = db.cursor()
    sql = '''insert into li_stu
(stuid, sex, uniid, uniname, proid, proname, scr, addscr, chiscr, mthscr, engscr, comscr, comjson)
values\n'''
    try:
        cursor.execute(sql+s)
        db.commit()
    except BaseException as e:
        print(e)
        db.rollback()


def multhreadgetstuinfo(link=['a', 'b']): # 多线程执行函数，攒52个人的sql语句一起插入，link是考试界面的链接列表
    s = requests.session()
    s.headers.update({'referer':r'https://www1.nm.zsks.cn/xxcx/gkcx/lqmaxmin21_2.jsp'})
    url = r'https://www1.nm.zsks.cn/xxcx/gkcx/lqmaxmin21_3.jsp?'
    sql = ''
    for ii in range(len(link)):
        ctt = s.get(url + link[ii], verify=False)
        anstable = TableInfo(ctt.content.decode())
        sql += dicttosql(anstable.getinfo())
        if ii % 52 == 0:
            sql += ';\n'
            sqladd(sql)
            sql = ''
        else:
            sql += ',\n'
        print(100 * ii / len(link))
        time.sleep(0.3)
    if len(sql) > 0:
        sql = sql[0:len(sql) - 2] + ';\n'
        sqladd(sql)


db = pymysql.connect(host='localhost', port=3306, user='root', password='52Dyd1314,.', database='gkbm2021')
cursor = db.cursor()
sql = '''select id, proid, proname from li_uni;'''
cursor.execute(sql)
uni = cursor.fetchall()  # 数据库中取得所有院校的理科招生专业代号
print('database completed!')
urllib3.disable_warnings()
session = requests.session()
session.headers.update({'referer':'https://www1.nm.zsks.cn/xxcx/gkcx/lqmaxmin_21.jsp'})  # 添加referer头
url = r'https://www1.nm.zsks.cn/xxcx/gkcx/lqmaxmin21_2.jsp?pcdm=3&kldm=B&yxdh=%s&zydh=%s&zymc=%s'

href = []  # 考生信息链接列表

print('收集考号中')
cnt = 0
with open("ksh_wen.txt", 'a+') as f:
    for i in uni:  #  应该优化为多线程
        i = (i[0].upper(), i[1].upper(), i[2])
        ctt = session.get(url % i, verify=False)  # 访问某学校某专业页面
        f.write(str(i) + '\n')
        f.flush()
        try:
            cttc = getnum(ctt.content.decode())
        except BaseException as e:
            print(e)
            continue;
        for j in cttc:
            href.append(j)
            f.write(str(j) + '\n')
            f.flush()
        print(str(i) + '    ' + str(100 * cnt / len(uni)))
        cnt += 1
f.close()

tr = []
for i in range(20):  # 应该优化为实时为每个线程分配任务量，否则会出现单一线程卡顿导致效率降低的情况
                     # 多线程从同一对象存取数据设计锁的概念，没学过不会，明年再学
    tr.append(threading.Thread(target=multhreadgetstuinfo, args=(href[int(len(href) / 20) * i: int(len(href) / 20) * (i+1)],)))
    tr[i].start()
tr.append(threading.Thread(target=multhreadgetstuinfo, args=(href[int(len(href) / 20) * 20: len(href)],)))
tr[20].start()

for i in range(20 + 1):  # 等待全部进程结束
    tr[i].join()
