import os,sys,pprint,json

sys.path.append(os.environ.get('PS_SITEPACKAGES'))
from PictureShop2.Shared import StyleUtils

from Qt import QtWidgets,QtCore,QtGui


################################################################################
# Data
################################################################################
BillTo = {
	'CMD':'Chris/Mona/Denise',
	'CM':'Chris/Mona',
	'EKBT':'Eric/Bre',
	'BK': 'Brad',
	'DK': 'Denise',
	'NS': 'Nancy',
	'CK': 'Chris',
	'JK': 'Jesse',
	'EK': 'Eric',
	'MQ': 'Mona',
	'BT': 'Bre',
	'F':'Family (Arleta House)',
	'Misc': 'Other'
}


################################################################################
# Dialogs
################################################################################
class RecieptCreator(QtWidgets.QDialog):
	createClicked = QtCore.Signal(dict)
	def __init__(self, recieptDir, **kwargs):
		super(RecieptCreator,self).__init__(parent = kwargs.get('parent'))
		self.setWindowTitle("Reciept Creator")

		self.lblDate = QtWidgets.QLabel('Date:')
		self.uiDate = QtWidgets.QDateEdit()
		self.lblStoreName = QtWidgets.QLabel('Store Name:')
		self.uiStoreName = QtWidgets.QLineEdit()
		self.uiCreate = QtWidgets.QPushButton('Create')
		self.uiCancel = QtWidgets.QPushButton('Cancel')

		self.uiDate.setCalendarPopup(True)
		self.uiDate.setDate(QtCore.QDate.currentDate())

		self.layMain = QtWidgets.QVBoxLayout()
		self.laySettings = QtWidgets.QHBoxLayout()
		self.layOperators = QtWidgets.QHBoxLayout()

		self.layMain.addLayout(self.laySettings)
		self.layMain.addLayout(self.layOperators)

		self.laySettings.addWidget(self.lblDate)
		self.laySettings.addWidget(self.uiDate)
		self.laySettings.addWidget(self.lblStoreName)
		self.laySettings.addWidget(self.uiStoreName)

		self.layOperators.addStretch()
		self.layOperators.addWidget(self.uiCreate)
		self.layOperators.addWidget(self.uiCancel)

		self.setLayout(self.layMain)

		self.uiCancel.clicked.connect(self.reject)
		self.uiStoreName.textEdited.connect(self.verifyInputs)
		self.uiDate.dateChanged.connect(self.verifyInputs)
		self.uiCreate.clicked.connect(self.createReciept)

		self.verifyInputs()

	def verifyInputs(self):
		storeName = self.uiStoreName.text()
		for char in '!@#$%^&*()_+=-[]}{:";,>.</?\\|':
			storeName = storeName.replace(char,'')
		storeName = storeName.replace(' ','-')
		
		if storeName != '':
			self.storeName = storeName
			self.uiCreate.setEnabled(True)
		else:
			self.uiCreate.setEnabled(False)

		pprint.pprint(dir(self.uiDate.dateTime().date()))
		day,month,year = (
			self.uiDate.dateTime().date().month(),
			self.uiDate.dateTime().date().day(),
			self.uiDate.dateTime().date().year()
		)

		self.date = '-'.join([str(day),str(month),str(year)])


	def createReciept(self):
		data = {}
		data['date'] = self.date
		data['storeName'] = self.storeName

		self.createClicked.emit(data)
		self.accept()


################################################################################
# Widgets
################################################################################
class MoneySpinner(QtWidgets.QWidget):
	def __init__(self):
		super(MoneySpinner,self).__init__()


class GroceryItemWidget(QtWidgets.QWidget):
	itemUpdated = QtCore.Signal(str)
	def __init__(self,**kwargs):
		super(GroceryItemWidget,self).__init__()

		# Data
		self.billingActions = []

		# Widget Construction
		self.lblItemName = QtWidgets.QLabel('Item Name:')
		self.uiItemName = QtWidgets.QLineEdit()
		self.lblPrice = QtWidgets.QLabel('Price:')
		self.uiPrice = QtWidgets.QLineEdit()
		self.lblCRV = QtWidgets.QLabel('CRV:')
		self.uiCRV = QtWidgets.QLineEdit()		
		self.uiBillTo = QtWidgets.QPushButton('Add Bill Recipient:')
		self.uiBillToMenu = QtWidgets.QMenu()
		self.lblBillist = QtWidgets.QLabel()
		self.uiTaxable = QtWidgets.QCheckBox('Taxable')

		# Widget settings
		self.uiBillTo.setMenu(self.uiBillToMenu)
		for k in sorted(BillTo.keys()):
			action = QtWidgets.QAction(BillTo[k],self)
			action.setCheckable(True)
			action.triggered.connect(self.updateBillToList)
			self.uiBillToMenu.addAction(action)
			self.billingActions.append(action)

		# Layout Creation
		self.layMain = QtWidgets.QHBoxLayout()

		for widge in [
			self.lblItemName,
			self.uiItemName,
			self.lblPrice,
			self.uiPrice,
			self.lblCRV,
			self.uiCRV,
			self.uiTaxable,
			self.uiBillTo,
			self.lblBillist
		]:
			self.layMain.addWidget(widge)

		self.setLayout(self.layMain)

		self.uiItemName.textEdited.connect(self.itemUpdated.emit)
		self.uiPrice.textEdited.connect(self.itemUpdated.emit)
		self.uiCRV.textEdited.connect(self.itemUpdated.emit)
		self.uiTaxable.stateChanged.connect(self.itemUpdated.emit)


	def clear(self):
		self.uiItemName.clear()
		self.uiPrice.clear()
		self.uiCRV.clear()
		self.uiTaxable.setChecked(False)
		self.lblBillist.setText('')

		for action in self.billingActions:
			action.setChecked(False)

		self.itemUpdated.emit('')


	def updateBillToList(self):
		billable = []
		for action in self.billingActions:
			if action.isChecked():
				for k in BillTo.keys():
					if BillTo[k] == action.text():
						billable.append(k)

		billList = '/'.join(sorted(billable))
		self.lblBillist.setText(billList)
		self.itemUpdated.emit('')

	def getData(self):
		data = {
			'itemName':self.uiItemName.text(),
			'itemPrice':self.uiPrice.text(),
			'itemCrv':self.uiCRV.text(),
			'itemTaxable':self.uiTaxable.isChecked(),
			'billTo':self.lblBillist.text()
		}

		return data

class RecieptBuddy_ItemList(QtWidgets.QWidget):
	recieptUpdated = QtCore.Signal()
	def __init__(self):
		super(RecieptBuddy_ItemList,self).__init__()
		self.rootItems = {}
		self.taxRate = 0

		# data
		self.RecieptDir = os.path.join(os.environ.get('ArletaHouse'),'tools','recieptBuddy','source','lib','reciepts')
		if not os.path.isdir(self.RecieptDir):
			os.makedirs(self.RecieptDir)

		# widget creation
		self.uiRecieptSelector = QtWidgets.QComboBox()
		self.uiPayTo = QtWidgets.QComboBox()
		self.uiTaxRate = QtWidgets.QLineEdit()
		self.uiGroceryTreeWidget = QtWidgets.QTreeWidget()
		self.uiTemplateGroup = QtWidgets.QGroupBox('Item Template')
		self.uiItemTemplate = GroceryItemWidget()
		self.uiAddItem = QtWidgets.QPushButton(StyleUtils.getIcon('add'),'Add Item')

		# widget settings
		for k in sorted(BillTo.keys()):
			self.uiPayTo.addItem(BillTo[k])
		self.uiAddItem.setEnabled(False)
		self.uiGroceryTreeWidget.setHeaderLabels(['Item Name', 'Item Price','CRV','Taxable','Item Total','Bill To'])
		# self.uiRecieptSelector.addItems(['None','Create New'])

		#Layout Construction
		self.layMain = QtWidgets.QVBoxLayout()
		self.layForm = QtWidgets.QFormLayout()
		self.layTemplate = QtWidgets.QVBoxLayout()
		self.layOperators = QtWidgets.QHBoxLayout()

		#layout settings
		self.layMain.addLayout(self.layForm)
		self.layMain.addWidget(self.uiTemplateGroup)

		self.layTemplate.addWidget(self.uiItemTemplate)
		self.layTemplate.addLayout(self.layOperators)

		self.layOperators.addStretch()
		self.layOperators.addWidget(self.uiAddItem)

		self.layForm.addRow('Reciept:',self.uiRecieptSelector)
		self.layForm.addRow('Pay To:',self.uiPayTo)
		self.layForm.addRow('Tax Rate:',self.uiTaxRate)
		self.layForm.addRow('Items:',self.uiGroceryTreeWidget)

		# layout application
		self.setLayout(self.layMain)
		self.uiTemplateGroup.setLayout(self.layTemplate)

		self.uiItemTemplate.itemUpdated.connect(self.verifyTemplate)
		self.uiAddItem.clicked.connect(self.addItem)
		self.uiRecieptSelector.currentIndexChanged.connect(self.openReciept)

		self.populateReciepts()


	def openReciept(self):
		if self.uiRecieptSelector.currentText() == 'New Reciept':
			creator = RecieptCreator(self.RecieptDir, parent = self)
			creator.createClicked.connect(self.createNewReciept)
			creator.exec_()

	def createNewReciept(self, data):
		data['taxRate'] = self.uiTaxRate.text()
		data['payableTo'] = self.uiPayTo.currentText()
		data['items'] = []

		filename = '_'.join([data['date'],data['storeName']])

		jsonFile = os.path.join(self.RecieptDir,filename + '.reciept')

		with open(jsonFile,'w') as jFile:
			json.dump(data, jFile, ensure_ascii=False, indent=4)

		self.populateReciepts()
		self.uiRecieptSelector.setCurrentIndex(self.uiRecieptSelector.findText(filename + '.reciept'))


	def populateReciepts(self):
		self.uiRecieptSelector.clear()
		files = os.listdir(self.RecieptDir)
		files.sort()
		files.reverse()

		self.uiRecieptSelector.addItem('')
		self.uiRecieptSelector.addItems(files)
		self.uiRecieptSelector.addItem('New Reciept')



	def verifyTemplate(self):
		data = self.uiItemTemplate.getData()
		print data

		valid = True
		for k in data.keys():
			if data[k] == '':
				valid = False

		self.uiAddItem.setEnabled(valid)


	def addItem(self, itemData = None):
		if data is None:
			itemData = self.uiItemTemplate.getData()

		itemTotal = float(itemData['itemPrice']) + float(itemData['itemCrv']) + (float(itemData['itemPrice'])*self.taxRate)

		if itemData['billTo'] not in self.rootItems.keys():
			self.createRootItem(itemData['billTo'])
			labels = [
				itemData['itemName'],
				itemData['itemPrice'],
				itemData['itemCrv'],
				str(itemData['itemTaxable']),
				str(itemTotal),
				itemData['billTo']
			]
			newItem = QtWidgets.QTreeWidgetItem(self.rootItems[itemData['billTo']],labels)			

		else:
			labels = [
				itemData['itemName'],
				itemData['itemPrice'],
				itemData['itemCrv'],
				str(itemData['itemTaxable']),
				str(itemTotal),
				itemData['billTo']
			]
			newItem = QtWidgets.QTreeWidgetItem(self.rootItems[itemData['billTo']],labels)

		self.uiItemTemplate.clear()
		self.recieptUpdated.emit()


	def createRootItem(self,itemName):
		newTreeRoot = QtWidgets.QTreeWidgetItem(self.uiGroceryTreeWidget,[itemName])
		self.rootItems[itemName] = newTreeRoot


class RecieptBuddy_BillPreview(QtWidgets.QWidget):
	def __init__(self):
		super(RecieptBuddy_BillPreview,self).__init__()

		self.uiBillGroup = QtWidgets.QGroupBox('Bill Preview')
		self.uiScrollArea = QtWidgets.QScrollArea()
		self.lblBill = QtWidgets.QLabel()

		# widget settings
		self.uiScrollArea.setWidget(self.lblBill)

		self.layMain = QtWidgets.QVBoxLayout()
		self.layBillGroup = QtWidgets.QVBoxLayout()

		self.layMain.addWidget(self.uiBillGroup)
		self.layBillGroup.addWidget(self.uiScrollArea)

		self.setLayout(self.layMain)	



################################################################################
# Main Tool
################################################################################
class RecieptBuddy_UI(QtWidgets.QMainWindow):
	def __init__(self):
		super(RecieptBuddy_UI,self).__init__()
		self.setWindowTitle('Reciept Buddy!')
		self.resize(900,800)

		self.uiCentralWidget = QtWidgets.QWidget()

		self.uiSplitter = QtWidgets.QSplitter()
		self.uiItemList = RecieptBuddy_ItemList()
		self.uiBillPreview = RecieptBuddy_BillPreview()
		self.uiGenerateItimized = QtWidgets.QPushButton('Generate Itemized Reciept')
		self.uiGenerateBill = QtWidgets.QPushButton('Generate Group Bill')

		# widgetSettings
		self.uiSplitter.setOrientation(QtCore.Qt.Vertical)
		self.uiSplitter.addWidget(self.uiItemList)
		self.uiSplitter.addWidget(self.uiBillPreview)

		# LayoutGeneration
		self.layMain = QtWidgets.QVBoxLayout()
		self.layOperators = QtWidgets.QHBoxLayout()

		# Layout settings
		self.layMain.addWidget(self.uiSplitter)
		self.layMain.addLayout(self.layOperators)

		self.layOperators.addStretch()
		self.layOperators.addWidget(self.uiGenerateItimized)
		self.layOperators.addWidget(self.uiGenerateBill)

		# Layout Assignment
		self.uiCentralWidget.setLayout(self.layMain)

		self.setCentralWidget(self.uiCentralWidget)

		self.uiItemList.recieptUpdated.connect(self.updateBillPreview)

	def updateBillPreview(self):
		print 'updating'


class RecieptBuddy(RecieptBuddy_UI):
	def __init__(self):
		super(RecieptBuddy,self).__init__()



################################################################################
# Unit Testing
################################################################################
def unitTest_Main():
    app = QtWidgets.QApplication(sys.argv)
    ex = RecieptBuddy()
    StyleUtils.setStyleSheet(ex)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
	unitTest_Main()