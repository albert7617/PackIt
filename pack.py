# uncompyle6 version 3.9.1
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.9.13 (tags/v3.9.13:6de2ca5, May 17 2022, 16:36:42) [MSC v.1929 64 bit (AMD64)]
# Embedded file name: pack.py
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAbstractItemView, QFileDialog, QMessageBox
from os import walk, path
from natsort import natsorted
from shutil import copy2

class FolderLineWidget(QtWidgets.QLineEdit):

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("lineEdit")
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls:
            if urls[0].scheme() == "file":
                event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls:
            if urls[0].scheme() == "file":
                event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls:
            if urls[0].scheme() == "file":
                filepath = str(urls[0].path())[1:]
                self.setText(filepath)


class FolderListWidget(QtWidgets.QListWidget):

    def __init__(self, type, parent=None):
        super(FolderListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)
        if event.mimeData().hasUrls:
            event.accept()

    def dropEvent(self, event):
        super().dropEvent(event)
        if event.mimeData().hasUrls:
            if len(event.mimeData().urls()) != 0:
                event.setDropAction(QtCore.Qt.CopyAction)
                event.accept()
                for url in event.mimeData().urls():
                    self.addItem(str(url.toLocalFile()))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            for item in self.selectedItems():
                self.takeItem(self.row(item))
        if event.key() == QtCore.Qt.Key_A and event.modifiers() == QtCore.Qt.ControlModifier:
            self.selectAll()

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item is None:
            print("Clicked on blank space")
        else:
            self.clearSelection()
            print(f"Clicked on item: {item.text()}")
        super(FolderListWidget, self).mousePressEvent(event)

    
    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item is None:
            self.selectAll()
            for item in self.selectedItems():
                self.takeItem(self.row(item))
        else:
            print(f"Double-clicked on item: {item.text()}")
        super(FolderListWidget, self).mouseDoubleClickEvent(event)

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    initProg = QtCore.pyqtSignal(int)
    tickProg = QtCore.pyqtSignal(int)

    def __init__(self, src, dst):
        super().__init__()
        self.src = src
        self.dst = dst

    @QtCore.pyqtSlot()
    def copyWork(self):  # A slot takes no params
        fileName = 1
        for srcPath in self.src:
            for dirPath, dirNames, fileNames in walk(srcPath):
                for f in fileNames:
                    fileName += 1

        self.initProg.emit(fileName)

        fileName = 1
        for srcPath in self.src:
            for dirPath, dirNames, fileNames in walk(srcPath):
                fileNames = natsorted(fileNames)
                for f in fileNames:
                    copy2(path.join(dirPath, f), path.join(self.dst, str(fileName).zfill(3) + path.splitext(f)[1]))
                    fileName += 1

            self.tickProg.emit(fileName)

        self.finished.emit()


class CopyProgressDiaglog(QtWidgets.QWidget):

    def __init__(self, src, dst):
        super().__init__()
        self.src = src
        self.dst = dst

        main_center_x = MainWindow.pos().x() + MainWindow.size().width() / 2
        main_center_y = MainWindow.pos().y() + MainWindow.size().height() / 2

        popup_width = 550
        popup_height = 100
        popup_x = int(main_center_x - popup_width / 2)
        popup_y = int(main_center_y - popup_height / 2)

        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setGeometry(30, 40, 500, 75)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.pbar)
        self.setLayout(self.layout)
        self.setGeometry(popup_x, popup_y, popup_width, popup_height)
        self.setWindowTitle('Progress Bar')

        self.obj = Worker(src, dst)
        self.obj.initProg.connect(self.on_count_init)
        self.obj.tickProg.connect(self.on_count_changed)
        self.obj.moveToThread(copyThread)
        copyThread.started.connect(self.obj.copyWork)

    def start_progress(self):  # To restart the progress every time
        self.show()
        copyThread.start()
        msg = QMessageBox()
        msg.setText("Done")
        msg.setWindowTitle("Info")
        msg.setStandardButtons(QMessageBox.Ok)
        QtWidgets.QApplication.beep()
        msg.exec_()

    def on_count_changed(self, value):
        self.pbar.setValue(value)
    
    def on_count_init(self, value):
        self.pbar.setRange(0, value)


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(619, 415)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = FolderLineWidget(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.openFileNameDialog)
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.listWidget = FolderListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.runButton = QtWidgets.QPushButton(self.centralwidget)
        self.runButton.setObjectName("runButton")
        self.runButton.clicked.connect(self.runButtonClick)
        self.verticalLayout.addWidget(self.runButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 619, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Pack it"))
        self.pushButton.setText(_translate("MainWindow", "Select Folder"))
        self.runButton.setText(_translate("MainWindow", "Run"))

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        fileName = QFileDialog.getExistingDirectory(None, "Open Directory", "", options=options)
        if fileName:
            self.lineEdit.setText(fileName)

    def runButtonClick(self):
        destination = self.lineEdit.text()
        if path.isdir(destination):
            fileName = 1
            for i in range(self.listWidget.count()):
                for dirPath, dirNames, fileNames in walk(self.listWidget.item(i).text()):
                    fileNames = natsorted(fileNames)
                    for f in fileNames:
                        copy2(path.join(dirPath, f), path.join(destination, str(fileName).zfill(3) + path.splitext(f)[1]))
                        fileName += 1

            msg = QMessageBox()
            msg.setText("Done")
            msg.setWindowTitle("Info")
            msg.setStandardButtons(QMessageBox.Ok)
            QtWidgets.QApplication.beep()
            msg.exec_()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    copyThread = QtCore.QThread()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

# okay decompiling pack.pyc