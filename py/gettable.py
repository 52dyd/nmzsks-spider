# 手动拷贝存在院校名称与代号的<table>保存在
import copy
import pymysql

class TableInfo:
    html_str = ''

    def __init__(self, htmlstr = '', startloc=''):
        self.html_str = htmlstr.lower()
        self.html_str = self.html_str.replace('\n', '')
        self.html_str = self.html_str.replace('\r', '')
        self.html_str = self.html_str.replace(' ', '')
        self.html_str = self.html_str.replace(r'<br>', '')
        self.html_str = self.html_str.replace(r'&nbsp;', ' ')
        if startloc != '' and self.html_str.find(start) != -1:
            self.html_str = self.html_str[self.html_str.find(start) + 7: len(self.html_str)]
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
                #elif self.html_str[0:4] == r'<div':
                #    self.html_str = self.html_str[self.html_str.find('</div>') + 6: len(self.html_str)]
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
        headlist = []
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
                for i in range(0, len(tmplist)):
                    tmpdict[headlist[i]] = tmplist[i]
                anslist.append(copy.deepcopy(tmpdict))
            else:
                self.setnxt()
            status = self.getnxt()

        self.setnxt()
        return anslist

    def getgradetable(self):
        anslist = []
        tmplist = []

        tmplist = self.getline()
        status = self.getnxt()
        while status != 2:
            self.setnxt()
            status = self.getnxt()

        while status != 6:
            if status == 2:
                tmplist.clear()
                tmplist = self.getline()
                for i in range(0, len(tmplist), 3):
                    anslist.append(copy.deepcopy(tmplist[i:i+3]))
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


f = open("test.in", 'r')
stu = TableInfo(f.read())
ctt = stu.gettable()

db = pymysql.connect(host='localhost', port=3306, user='root', password='52Dyd1314,.', database='gkbm2021')
cursor = db.cursor()
sql = '''insert into university
(id, name)
values
('%s', '%s');'''
for i in ctt:
    try:
        cursor.execute(sql % (i['院校代号'], i['院校名称']))
        db.commit()
    except BaseException as e:
        print(e)
        db.rollback()
