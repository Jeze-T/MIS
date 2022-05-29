import sys
from PyQt5 import QtCore, QtWidgets, QtCore
from PyQt5.QtCore import *     #Qt
from PyQt5.QtWidgets import *   #QMenu

import pymysql

from mawin import Ui_MainWindow as Hello_Ui
from login import Ui_MainWindow as Login_Ui
from op import Ui_MainWindow as Operate_Ui
from view import Ui_MainWindow as View_Ui
from again import Ui_MainWindow as Again_Ui
from inse import Ui_QMainWindow as Inse_Ui
from delet import Ui_MainWindow as Delet_Ui

# 主窗口
class HelloWindow(QtWidgets.QMainWindow, Hello_Ui):
    switch_window1 = QtCore.pyqtSignal()
    switch_window2 = QtCore.pyqtSignal()

    def __init__(self):
        super(HelloWindow, self).__init__()
        self.setupUi(self)
        self.queryButton.clicked.connect(self.goView)
        self.manageButton.clicked.connect(self.goLogin)

    def goLogin(self):
        self.switch_window1.emit()

    def goView(self):
        self.switch_window2.emit()


# 登录窗口
class LoginWindow(QtWidgets.QMainWindow, Login_Ui):
    switch_window1 = QtCore.pyqtSignal()
    switch_window2 = QtCore.pyqtSignal()
    switch_window3 = QtCore.pyqtSignal()

    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setupUi(self)
        self.okButton.clicked.connect(self.ok)
        self.cancelButton.clicked.connect(self.cancel)

    def ok(self):
        username = self.userText.text()
        password = self.pwdText.text()
        # 创建数据库连接
        conn = pymysql.connect(
            host='127.0.0.1',  # 连接主机, 默认127.0.0.1
            user='root',  # 用户名
            passwd='mysql',  # 密码
            port=3306,  # 端口，默认为3306
            db='sxnb19031102',  # 数据库名称
            charset='utf8'  # 字符编码
        )
        # 生成游标对象 cursor
        cursor = conn.cursor()
        if (cursor.execute("SELECT * FROM user WHERE username='%s' AND password='%s'" % (username, password))):
            self.switch_window1.emit()
        else:
            #print("密码错误！！")
            self.switch_window3.emit()
        cursor.close()
        conn.close()

    def cancel(self):
        self.switch_window2.emit()


class AgainWindow(QtWidgets.QMainWindow, Again_Ui):
    def __init__(self, parent=None):
        super(AgainWindow, self).__init__(parent)
        self.setupUi(self)


# 操作窗口
class OperateWindow(QtWidgets.QMainWindow, Operate_Ui):
    switch_window1 = QtCore.pyqtSignal()
    def __init__(self):
        super(OperateWindow, self).__init__()
        self.setupUi(self)
        self.exitButton.clicked.connect(self.exit)
        self.pushButton.clicked.connect(self.que)
        self.tableWidget.itemDoubleClicked.connect(self.updat)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  ######允许右键产生子菜单
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单

        self.modi = ''

        # 数据库连接对象
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password="mysql", db="sxnb19031102")
        # 游标对象
        self.cur = self.conn.cursor()

        # 查询的sql语句
        sql = "SELECT * FROM flight"
        self.cur.execute(sql)
        # 获取查询到的数据, 是以二维元组的形式存储的, 所以读取需要使用 data[i][j] 下标定位
        self.data = self.cur.fetchall()

        # 遍历二维元组, 将 id 和 name 显示到界面表格上
        x = 0
        for i in self.data:
            y = 0
            for j in i:
                self.tableWidget.setItem(x, y, QtWidgets.QTableWidgetItem(str(self.data[x][y])))
                y = y + 1
            x = x + 1

    def que(self):
        self.tableWidget.clearContents()

        self.id = self.lineEdit.text()
        self.da = self.dateEdit.date().toString('yyyy-MM-dd')
        # print(self.id)

        sql = "SELECT * FROM flight where idflight = '%s' and dateflight = '%s'" % (self.id, self.da)
        self.cur.execute(sql)  # 返回值是查询到的数据数量
        self.data = self.cur.fetchall()
        # print(self.data)
        x = 0
        for i in self.data:
            y = 0
            for j in i:
                self.tableWidget.setItem(x, y, QtWidgets.QTableWidgetItem(str(self.data[x][y])))
                y = y + 1
            x = x + 1

    def generateMenu(self, pos):
        row_num = -1
        for i in self.tableWidget.selectionModel().selection().indexes():
            row_num = i.row()

        if row_num < 9:
            menu = QMenu()
            item1 = menu.addAction(u"删除该行")
            action = menu.exec_(self.tableWidget.mapToGlobal(pos))
            if action == item1:
                self.id = self.tableWidget.item(row_num, 0).text()
                self.da = self.tableWidget.item(row_num, 3).text()
                sql = "DELETE FROM flight where idflight = '%s' and dateflight = '%s'" % (self.id, self.da)
                try:
                    self.cur.execute(sql)
                    self.conn.commit()
                    self.switch_window1.emit()
                except:
                    print("expection!")
                    self.conn.rollback()

            else:
                return

    def updat(self, Item=None):
        if Item is None:
            return
        else:
            self.row = Item.row()  # 获取行数
            self.col = Item.column()  # 获取列数 注意是column而不是col哦
            self.id = self.tableWidget.item(self.row, 0).text()
            self.da = self.tableWidget.item(self.row, 3).text()
            self.modivalue = self.lineEdit1.text()
            self.matching_method(self.col)

        sql = " UPDATE flight SET %s = '%s' where idflight = '%s' and dateflight = '%s'" % (self.modi,self.modivalue, self.id, self.da)
        try:
            self.cur.execute(sql)
            self.conn.commit()
            self.tableWidget.item(self.row, self.col).setText(self.modivalue)
        except:
            print("expection!")
            self.conn.rollback()

    def exit(self):
        sys.exit(0)
        self.cur.close()
        self.conn.close()

    def case0(self):  # 第一种情况执行的函数
        self.modi = 'idflight'

    def case1(self):  # 第一种情况执行的函数
        self.modi = 'src'

    def case2(self):  # 第二种情况执行的函数
        self.modi = 'des'

    def case3(self):  # 第三种情况执行的函数
        self.modi = 'dateflight'

    def case4(self):  # 第三种情况执行的函数
        self.modi = 'starttime'

    def case5(self):  # 第三种情况执行的函数
        self.modi = 'endtime'

    def case6(self):  # 第三种情况执行的函数
        self.modi = 'remain_seats'

    def case7(self):  # 第三种情况执行的函数
        self.modi = 'fares'

    def case8(self):  # 第三种情况执行的函数
        self.modi = 'discount_nums'

    def case9(self):  # 第三种情况执行的函数
        self.modi = 'discount'

    def case10(self):  # 第三种情况执行的函数
        self.modi = 'ubordinate_company'

    def default(self):  # 默认情况下执行的函数
        print('No such case')

    def matching_method(self, switch):
        switchs = {
            0: self.case0,
            1: self.case1,
            2: self.case2,
            3: self.case3,
            4: self.case4,
            5: self.case5,
            6: self.case6,
            7: self.case7,
            8: self.case8,
            9: self.case9,
            10: self.case10
        }
        switchs.get(switch, self.default)()

class InseWindow(QtWidgets.QMainWindow, Inse_Ui):
    switch_window1 = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(InseWindow, self).__init__(parent)
        self.setupUi(self)
        self.B_inse.clicked.connect(self.inse)

        # 数据库连接对象
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password="mysql", db="sxnb19031102")
        # 游标对象
        self.cur = self.conn.cursor()

    def inse(self):
        self.id = self.lineE_id.text()
        self.srcc = self.lineE_srcc.text()
        self.dst = self.lineE_dst.text()
        self.da = self.dateEdit.date().toString('yyyy-MM-dd')
        self.start = self.timeE_start.time().toString('mm:ss')
        self.end = self.timeE_end.time().toString('mm:ss')
        self.compa = self.lineE_compa.text()

        sql = "INSERT INTO flight (idflight, src, des, dateflight, starttime, endtime, ubordinate_company) \
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
              % (self.id, self.srcc, self.dst, self.da, self.start, self.end, self.compa)
        if self.id != '':
            try:
                self.cur.execute(sql)
                self.conn.commit()
                self.switch_window1.emit()
            except:
                print("expection!")
                self.conn.rollback()

# 查询窗口
class ViewWindow(QtWidgets.QMainWindow, View_Ui):
    def __init__(self):
        super(ViewWindow, self).__init__()
        self.setupUi(self)
        self.exitButton.clicked.connect(self.exit)
        self.pushButton.clicked.connect(self.que)
        self.id = self.lineEdit.setText('')

        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password="mysql", db="sxnb19031102")
        # 游标对象
        self.cur = self.conn.cursor()

        # 查询的sql语句
        sql = "SELECT * FROM flight"
        self.cur.execute(sql)
        # 获取查询到的数据, 是以二维元组的形式存储的, 所以读取需要使用 data[i][j] 下标定位
        self.data = self.cur.fetchall()
        # 打印测试
        #print(self.data)

        # 遍历二维元组, 将 id 和 name 显示到界面表格上
        x = 0
        for i in self.data:
            y = 0
            for j in i:
                self.tableWidget.setItem(x, y, QtWidgets.QTableWidgetItem(str(self.data[x][y])))
                y = y + 1
            x = x + 1

    def que(self):
        self.tableWidget.clearContents()

        self.id = self.lineEdit.text()
        self.da = self.dateEdit.date().toString('yyyy-MM-dd')
        #print(self.id)

        sql = "SELECT * FROM flight where idflight = '%s' and dateflight = '%s'" %(self.id,self.da)
        self.cur.execute(sql)  # 返回值是查询到的数据数量
        self.data = self.cur.fetchall()
        #print(self.data)
        x = 0
        for i in self.data:
            y = 0
            for j in i:
                self.tableWidget.setItem(x, y, QtWidgets.QTableWidgetItem(str(self.data[x][y])))
                y = y + 1
            x = x + 1

    def exit(self):
        sys.exit(0)
        self.cur.close()
        self.conn.close()


# 利用一个控制器来控制页面的跳转
class Controller:
    def __init__(self):
        self.hello = HelloWindow()
        self.login = LoginWindow()
        self.operate = OperateWindow()
        self.view = ViewWindow()
        self.again = AgainWindow()
        self.inse = InseWindow()


    def show_hello(self):
        self.hello = HelloWindow()
        self.hello.switch_window1.connect(self.show_login)
        self.hello.switch_window2.connect(self.show_view)
        self.hello.show()
        self.login.close()
        self.again.close()
        self.operate.close()
        self.inse.close()
        self.view.close()

    def show_login(self):
        self.login = LoginWindow()
        self.login.switch_window1.connect(self.show_operate)
        self.login.switch_window2.connect(self.show_hello)
        self.login.switch_window3.connect(self.show_again)
        self.login.show()
        self.again.close()
        self.hello.close()
        self.operate.close()
        self.inse.close()
        self.view.close()

    def show_again(self):
        self.again = AgainWindow()
        self.again.B_again.clicked.connect(self.show_login)
        self.again.show()
        self.operate.close()
        self.inse.close()
        self.hello.close()
        self.login.close()
        self.view.close()

    def show_operate(self):
        self.operate = OperateWindow()
        self.operate.switch_window1.connect(self.show_operate)
        self.operate.pushButton_5.clicked.connect(self.show_operate)
        self.operate.pushButton_3.clicked.connect(self.show_inse)
        self.operate.show()
        self.inse.close()
        self.hello.close()
        self.login.close()
        self.again.close()
        self.view.close()

    def show_inse(self):
        self.inse = InseWindow()
        self.inse.switch_window1.connect(self.show_operate)
        self.inse.B_cancel.clicked.connect(self.show_operate)
        self.inse.show()
        self.operate.close()
        self.hello.close()
        self.login.close()
        self.again.close()
        self.view.close()

    def show_view(self):
        self.view = ViewWindow()
        self.view.pushButton_5.clicked.connect(self.show_view)
        self.view.show()
        self.hello.close()
        self.login.close()
        self.again.close()
        self.operate.close()
        self.inse.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.show_hello()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
