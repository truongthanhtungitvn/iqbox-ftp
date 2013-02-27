import os
import sys
import signal

from PySide.QtCore import Qt, Slot, Signal, QSettings
from PySide.QtGui import QWidget, QMainWindow, QApplication
from PySide.QtGui import QPushButton, QLabel, QLineEdit, QFont, QFileDialog
from PySide.QtGui import QHBoxLayout, QVBoxLayout, QPixmap, QFrame

import resources
import syncapp


SettingsKeys = {
    'host': 'Host',
    'username': 'Username',
    'passwd': 'Password',
    'localdir': 'LocalDir'}


def get_settings():
    return QSettings('IQStorage', 'FTPSync')


class SyncWindow(QMainWindow):
    
    failedLogIn = Signal()
    
    def __init__(self, parent=None):
        super(SyncWindow, self).__init__(parent)
        
        self.setStyleSheet('SyncWindow {background: white}')
        self.setWindowTitle('FTPSync')
        self.loginView()
        
    def loginView(self):
        login = LoginView()
        
        login.login.connect(self.onLogin)
        self.failedLogIn.connect(login.onFailedLogIn)
        
        self.setCentralWidget(login)
        self.setFixedSize(login.size())
        
    def syncView(self):
        syncview = SyncView()
        
        self.setCentralWidget(syncview)
        self.setFixedSize(syncview.size())
        
    @Slot(str, str, str)
    def onLogin(self, host, username, passwd):
        self.sync = syncapp.get_ftp(False, host)
        
        try:
            loginResponse = self.sync.login(username, passwd)
        except:
            self.failedLogIn.emit()
        else:
            print loginResponse
            if '230' in loginResponse:
                self.syncView()
            else:
                self.failedLogIn.emit()


class View(QWidget):
    
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        
    @staticmethod
    def labelsFont():
        return View.font(True)
        
    @staticmethod
    def fieldsFont():
        return View.font(False)
        
    @staticmethod
    def font(bold):
        font = QFont('', 9, 50, False)
        font.setBold(bold)
        
        return font
        
    def setLogo(self):
        logoPixmap = QPixmap(':/resources/logo.png')
        self.iconLabel = QLabel(self)
        self.iconLabel.setPixmap(logoPixmap)
        self.iconLabel.setGeometry(20, 20, logoPixmap.width(), logoPixmap.height())
        
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine);
        self.line.setFrameShadow(QFrame.Sunken);


class LoginView(View):
    login = Signal((str, str, str,))
    
    def __init__(self, parent=None):
        super(LoginView, self).__init__(parent)
        
        self.createWidgets()
        self.createLayouts()
        self.setFixedSize(250, 325)
        
    def createLayouts(self):
        mainLayout = QHBoxLayout()
        fieldsLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        
        mainLayout.addStretch(20)
        
        fieldsLayout.addStretch(80)
        #fieldsLayout.addWidget(self.iconLabel)
        fieldsLayout.addWidget(self.line)
        fieldsLayout.addStretch(20)
        fieldsLayout.addWidget(self.hostLabel)
        fieldsLayout.addWidget(self.hostEdit)
        fieldsLayout.addWidget(self.usernameLabel)
        fieldsLayout.addWidget(self.usernameEdit)
        fieldsLayout.addWidget(self.passwdLabel)
        fieldsLayout.addWidget(self.passwdEdit)
        fieldsLayout.addStretch(30)
        
        buttonLayout.addStretch(50)
        buttonLayout.addWidget(self.loginButton, 50, Qt.AlignRight)
        
        fieldsLayout.addLayout(buttonLayout)
        fieldsLayout.addStretch(20)
        
        mainLayout.addLayout(fieldsLayout, 30)
        mainLayout.addStretch(20)
        
        self.setLayout(mainLayout)
        
    def createWidgets(self):
        fieldsWidth = 200
        labelsFont = View.labelsFont()
        fieldsFont = View.fieldsFont()
        self.setLogo()
        
        self.hostLabel = QLabel(self)
        self.hostEdit = QLineEdit(self)
        self.hostLabel.setText('FTP Location')
        self.hostLabel.setFont(labelsFont)
        self.hostEdit.setFixedWidth(fieldsWidth)
        self.hostEdit.setFont(fieldsFont)
        
        self.usernameLabel = QLabel(self)
        self.usernameEdit = QLineEdit(self)
        self.usernameLabel.setText('Username')
        self.usernameLabel.setFont(labelsFont)
        self.usernameEdit.setFixedWidth(fieldsWidth)
        self.usernameEdit.setFont(fieldsFont)
        
        self.passwdLabel = QLabel(self)
        self.passwdEdit = QLineEdit(self)
        self.passwdLabel.setText('Password')
        self.passwdLabel.setFont(labelsFont)
        self.passwdEdit.setFixedWidth(fieldsWidth)
        self.passwdEdit.setEchoMode(QLineEdit.Password)
        self.passwdEdit.setFont(fieldsFont)
        
        self.loginButton = QPushButton(self)
        self.loginButton.setText('Login')
        self.loginButton.setFont(labelsFont)
        self.loginButton.setFixedWidth(fieldsWidth / 2)
        self.loginButton.setStyleSheet('')
        self.loginButton.clicked.connect(self.onLoginClicked)
        
        settings = get_settings()
        
        self.hostEdit.setText(settings.value(SettingsKeys['host'], ''))
        self.usernameEdit.setText(settings.value(SettingsKeys['username'], ''))
        self.passwdEdit.setText(settings.value(SettingsKeys['passwd'], ''))
        
    @Slot()
    def onLoginClicked(self):
        host = self.hostEdit.text()
        username = self.usernameEdit.text()
        passwd = self.passwdEdit.text()
        
        print 'Logging in: %s, %s, %s' % (host, username, passwd)
        
        if len(host) > 0:
            settings = get_settings()
            
            settings.setValue(SettingsKeys['host'], host)
            settings.setValue(SettingsKeys['username'], username)
            settings.setValue(SettingsKeys['passwd'], passwd)
            
            self.setEnabled(False)
            self.login.emit(host.strip(), username, passwd)
            
    @Slot()
    def onFailedLogIn(self):
        self.setEnabled(True)
        
        
class SyncView(View):
    
    def __init__(self, parent=None):
        super(SyncView, self).__init__(parent)
        
        self.createWidgets()
        self.createLayouts()
        self.setFixedSize(580, 325)

    def createLayouts(self):
        mainLayout = QHBoxLayout()
        fieldsLayout = QVBoxLayout()
        pathLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()
        
        mainLayout.addStretch(10)
        
        fieldsLayout.addStretch(50)
        #fieldsLayout.addWidget(self.iconLabel)
        fieldsLayout.addWidget(self.line)
        
        fieldsLayout.addWidget(self.localdirLabel) 
        pathLayout.addWidget(self.localdirEdit)
        pathLayout.addWidget(self.browseButton)
        fieldsLayout.addLayout(pathLayout)
        
        buttonLayout.addStretch(50)
        buttonLayout.addWidget(self.syncButton, 50, Qt.AlignRight)
        
        fieldsLayout.addLayout(buttonLayout)
        fieldsLayout.addStretch(100)

        mainLayout.addLayout(fieldsLayout, 60)
        mainLayout.addStretch(10)
        
        self.setLayout(mainLayout)
        
    def createWidgets(self):
        fieldsWidth = 450
        labelsFont = View.labelsFont()
        fieldsFont = View.fieldsFont()
        
        self.setLogo()
        
        self.localdirLabel = QLabel(self)
        self.localdirEdit = QLineEdit(self)
        self.localdirLabel.setText('Choose a directory')
        self.localdirLabel.setFont(labelsFont)
        self.localdirEdit.setFixedWidth(fieldsWidth)
        self.localdirEdit.setReadOnly(True)
        self.localdirEdit.setFont(fieldsFont)
        
        self.browseButton = QPushButton(self)
        self.browseButton.setText('Browse')
        self.browseButton.setFont(labelsFont)
        
        self.syncButton = QPushButton(self)
        self.syncButton.setText('Sync')
        self.syncButton.setFont(labelsFont)
        
        self.browseButton.clicked.connect(self.onBrowseClicked)
        self.syncButton.clicked.connect(self.onSyncClicked)
        
        settings = get_settings()
        self.localdirEdit.setText(settings.value(SettingsKeys['localdir'], ''))
        
    @Slot()
    def onBrowseClicked(self):
        localdir = QFileDialog.getExistingDirectory()
        
        print 'Localdir', localdir
        if len(localdir) > 0:
            localdir = os.path.join(localdir, 'FTPSync')
            get_settings().setValue(SettingsKeys['localdir'], localdir)
            self.localdirEdit.setText(localdir)
            
    @Slot()
    def onSyncClicked(self):
        pass
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SyncWindow()
    font = QFont('', 12, 50, False)
    
    app.setFont(font)
    window.show()
    sys.exit(app.exec_())
