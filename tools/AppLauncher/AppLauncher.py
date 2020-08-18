import os,sys,json,pprint,getpass,subprocess
sys.path.append(os.path.join(os.environ.get('ArletaHouse'),'site-packages'))
from Shared import StyleUtils

from Qt import QtCore,QtGui,QtWidgets


################################################################################
# widgets
################################################################################
class AppWidget(QtWidgets.QWidget):
	def __init__(self, **kwargs):
		super(AppWidget,self).__init__(parent = kwargs.get('parent'))
		self.resize(150,150)
		self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
		self.appData = kwargs.get('appData')
		print self.appData

		self.uiFrame = QtWidgets.QFrame()
		self.uiWidgetLogo = QtWidgets.QLabel()
		self.lblAppName = QtWidgets.QLabel(self.appData['appName'])
		self.uiProfile = QtWidgets.QComboBox()
		self.uiButton = QtWidgets.QPushButton()

		self.uiWidgetLogo.setPixmap(self.getIcon())
		self.uiWidgetLogo.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
		self.lblAppName.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
		self.uiWidgetLogo.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.lblAppName.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		self.uiButton.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))

		self.uiProfile.addItems(self.appData['profiles'].keys())

		self.layMain = QtWidgets.QHBoxLayout()
		self.layFrame = QtWidgets.QGridLayout()

		self.layMain.setContentsMargins(10,10,10,10)

		self.layFrame.addWidget(self.uiButton,1,0,2,1)
		self.layFrame.addWidget(self.uiWidgetLogo,1,0,1,1)
		self.layFrame.addWidget(self.lblAppName,0,0,1,1)
		self.layFrame.addWidget(self.uiProfile,2,0,1,1)

		self.layMain.addWidget(self.uiFrame)

		self.setLayout(self.layMain)
		self.uiFrame.setLayout(self.layFrame)

		self.uiButton.clicked.connect(self.launchApp)


	def launchApp(self):
		tokenData = {'<USER>':getpass.getuser()}

		profile = self.uiProfile.currentText()
		appPath = self.appData['profiles'][profile]['filepath']

		for token in tokenData.keys():
			appPath = appPath.replace(token,tokenData[token])

		if self.appData['type'] == 'pythonScript':
			cmd = 'python "{}"'.format(appPath)
			subprocess.Popen(cmd)

		if self.appData['type'] == 'executable':
			os.startfile(appPath)

		if self.appData['type'] == 'steamGame':
			os.startfile(appPath)





	def getIcon(self):
		iconDir = os.path.join(
			os.environ.get('ArletaHouse'),
			'tools',
			'AppLauncher',
			'resources',
			'appicons'
		)

		return os.path.join(iconDir,self.appData['appIcon'])



################################################################################
# DIALOGS
################################################################################



################################################################################
# Main Tool
################################################################################
class AppLauncher_UI(QtWidgets.QMainWindow):
	def __init__(self):
		super(AppLauncher_UI,self).__init__()
		self.setWindowTitle('Arleta House: App Launcher | 0.0.01')
		self.resize(400,400)

		self.centralWidget = QtWidgets.QScrollArea()

		self.layCentral = QtWidgets.QGridLayout()

		self.centralWidget.setLayout(self.layCentral)

		self.setCentralWidget(self.centralWidget)


class AppLauncher(AppLauncher_UI):
	def __init__(self):
		super(AppLauncher,self).__init__()
		appConfig = os.path.join(os.environ.get('ArletaHouse'),'tools','AppLauncher','apps.config')

		with open(appConfig,'r') as jFile:
			self.appData = json.load(jFile)

		pprint.pprint(self.appData)
		self.addApps()

	def addApps(self):
		columnCounter = 0
		rowCounter = 0

		for k in sorted(self.appData.keys()):
			appWidge = AppWidget(appData = self.appData[k])

			self.layCentral.addWidget(appWidge,rowCounter,columnCounter,1,1)

			columnCounter += 1

			if columnCounter > 2:
				columnCounter = 0
				rowCounter += 1

		self.layCentral.setRowStretch(rowCounter + 1,1)
		self.layCentral.setColumnStretch(3,1)

		


################################################################################
# UnitTesting
################################################################################
def unitTest_main():
    app = QtWidgets.QApplication(sys.argv)
    ex = AppLauncher()
    StyleUtils.setStyleSheet(ex)
    ex.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
	unitTest_main()