import os,sys

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
# Widgets
################################################################################
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


	def verifyTemplate(self):
		data = self.uiItemTemplate.getData()
		print data

		valid = True
		for k in data.keys():
			if data[k] == '':
				valid = False

		self.uiAddItem.setEnabled(valid)


	def addItem(self):
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