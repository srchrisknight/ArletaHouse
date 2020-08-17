import os,sys,pprint,json,time,datetime
from shutil import copyfile
from inspect import getsourcefile
sys.path.append(os.path.dirname(os.path.abspath(getsourcefile(lambda:0))))
sys.path.append(os.path.join(os.environ.get('ArletaHouse'),'site-packages'))
from Shared import StyleUtils
import RecieptParser
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
# Items
################################################################################
class GroceryTreeItem(QtWidgets.QTreeWidgetItem):
	def __init__(self, *args, **kwargs):
		super(GroceryTreeItem,self).__init__(*args)
		self.parentWidget = kwargs.get('parentWidget')
		self.itemData = kwargs.get('itemData')
		self.hasNote = False
		if self.itemData['itemNote'] != '':
			self.hasNote = True
			self.setIcon(0,StyleUtils.getIcon('alert-triangle-orange'))

		self.parentWidget.taxUpdated.connect(self.updateTotal)

		labels = [
				self.itemData['itemName'],
				self.itemData['itemPrice'],
				self.itemData['itemCrv'],
				str(self.itemData['itemTaxable']),
				str(0),
				str(self.itemData['itemTotal']),
				self.itemData['billTo']
			]

		for i in range(len(labels)):
			self.setText(i,labels[i])

		self.updateTotal()

	def setNote(self, note):
		if note != '':
			self.hasNote = True
			self.itemData['itemNote'] = note
			self.setIcon(0,StyleUtils.getIcon('alert-triangle-orange'))
		else:
			self.itemData['itemNote'] = ''
			self.setIcon(0,QtGui.QIcon())


	def updateTotal(self):
		price = float(self.itemData['itemPrice'])
		crv = float(self.itemData['itemCrv'])

		taxRate = self.parentWidget.taxRate
		if str(self.itemData['itemTaxable']) == 'True':
			taxMultiplier = 1 + (taxRate/100.0)

			total = (price + crv) * taxMultiplier
			tax = total - (price + crv)
			self.setText(5,str(round(total,2)))
			self.setText(4,str(round(tax,2)))
		else:
			total = price + crv
			self.setText(5,str(total))
			self.setText(4,str(0))


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


class ItemEditorDialog(QtWidgets.QDialog):
	def __init__(self,**kwargs):
		super(ItemEditorDialog,self).__init__(parent = kwargs.get('parent'))
		self.setWindowTitle('Grocery Item Editor')
		self.resize(600,100)

		# data
		self.listItem = kwargs.get('listItem')

		# widget creation
		self.uiItemTemplate = GroceryItemWidget()
		self.uiCommit = QtWidgets.QPushButton('Commit')
		self.uiCancel = QtWidgets.QPushButton('Cancel')

		# widgetSettings
		self.uiItemTemplate.setData(self.listItem.itemData)

		# layout creation
		self.layMain = QtWidgets.QVBoxLayout()
		self.layOperators = QtWidgets.QHBoxLayout()

		# layout settings
		self.layOperators.addStretch()
		self.layOperators.addWidget(self.uiCommit)
		self.layOperators.addWidget(self.uiCancel)

		self.layMain.addWidget(self.uiItemTemplate)
		self.layMain.addLayout(self.layOperators)

		# layout assignment
		self.setLayout(self.layMain)

		# signals
		self.uiCancel.clicked.connect(self.reject)
		self.uiCommit.clicked.connect(self.acceptChanges)

	def acceptChanges(self):
		itemData = self.uiItemTemplate.getData()
		print itemData
		self.parent().addItem(itemData = self.uiItemTemplate.getData())
		self.parent().removeItem(listItem = self.listItem)
		self.accept()


class NoteEditor(QtWidgets.QDialog):
	def __init__(self,**kwargs):
		super(NoteEditor,self).__init__(parent = kwargs.get('parent'))
		self.setWindowTitle('Note Editor')
		self.resize(400,400)

		# data
		noteData = kwargs.get('noteData','')

		# widget creation
		self.uiNote = QtWidgets.QTextEdit()
		self.uiCommit = QtWidgets.QPushButton(StyleUtils.getIcon('check'),'Commit')
		self.uiCancel = QtWidgets.QPushButton(StyleUtils.getIcon('close'),'Cancel')

		# widgetSettings
		self.uiNote.setText(noteData)

		# layout creation
		self.layMain = QtWidgets.QVBoxLayout()
		self.layOperators = QtWidgets.QHBoxLayout()

		# lay settings
		self.layOperators.addStretch()
		self.layOperators.addWidget(self.uiCommit)
		self.layOperators.addWidget(self.uiCancel)

		self.layMain.addWidget(self.uiNote)
		self.layMain.addLayout(self.layOperators)

		# layout assignment
		self.setLayout(self.layMain)

		# signals
		self.uiCancel.clicked.connect(self.reject)
		self.uiCommit.clicked.connect(self.updateNote)


	def updateNote(self):
		self.parent().setNote(self.uiNote.toPlainText())
		self.parent().itemUpdated.emit('')
		self.accept()


################################################################################
# Widgets
################################################################################
class GroceryItemWidget(QtWidgets.QWidget):
	itemUpdated = QtCore.Signal(str)
	def __init__(self,**kwargs):
		super(GroceryItemWidget,self).__init__()
		self.note = ''

		# Data
		self.billingActions = []

		# Widget Construction
		self.lblItemName = QtWidgets.QLabel('Item Name:')
		self.uiItemName = QtWidgets.QLineEdit()
		self.lblPrice = QtWidgets.QLabel('Price:')
		self.uiPrice = QtWidgets.QDoubleSpinBox()
		self.lblCRV = QtWidgets.QLabel('CRV:')
		self.uiCRV = QtWidgets.QDoubleSpinBox()		
		self.uiBillTo = QtWidgets.QPushButton('Add Bill Recipient:')
		self.uiBillToMenu = QtWidgets.QMenu()
		self.lblBillist = QtWidgets.QLabel()
		self.uiTaxable = QtWidgets.QCheckBox('Taxable')
		self.uiEditNote = QtWidgets.QPushButton()

		# Widget settings
		self.uiBillTo.setMenu(self.uiBillToMenu)
		for k in sorted(BillTo.keys()):
			action = QtWidgets.QAction(BillTo[k],self)
			action.setCheckable(True)
			action.triggered.connect(self.updateBillToList)
			self.uiBillToMenu.addAction(action)
			self.billingActions.append(action)
		self.uiEditNote.setIcon(StyleUtils.getIcon('edit'))
		self.uiEditNote.setToolTip('View/Edit Notes')

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
			self.lblBillist,
			self.uiEditNote
		]:
			self.layMain.addWidget(widge)

		self.setLayout(self.layMain)

		self.uiItemName.textEdited.connect(self.itemUpdated.emit)
		self.uiPrice.valueChanged.connect(self.itemUpdated.emit)
		self.uiCRV.valueChanged.connect(self.itemUpdated.emit)
		self.uiTaxable.stateChanged.connect(self.itemUpdated.emit)
		self.uiEditNote.clicked.connect(self.addNote)


	def addNote(self):
		noteEditor = NoteEditor(noteData = self.note, parent = self)
		noteEditor.exec_()


	def setNote(self,note):
		self.note = note


	def clear(self):
		self.uiItemName.clear()
		self.uiPrice.setValue(0)
		self.uiCRV.setValue(0)
		self.uiTaxable.setChecked(False)
		self.lblBillist.setText('')
		self.note = ''

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
			'itemPrice':str(self.uiPrice.value()),
			'itemCrv':str(self.uiCRV.value()),
			'itemTaxable':self.uiTaxable.isChecked(),
			'billTo':self.lblBillist.text(),
			'itemNote':self.note
		}

		return data

	def setData(self,data):
		self.uiItemName.setText(data['itemName'])
		self.uiPrice.setValue(float(data['itemPrice']))
		self.uiCRV.setValue(float(data['itemCrv']))
		self.uiTaxable.setChecked(str(data['itemTaxable']) == 'True')

		for initials in data['billTo'].split('/'):
			for action in self.billingActions:
				if action.text() == BillTo[initials]:
					action.setChecked(True)

		self.updateBillToList()



class RecieptBuddy_RecieptManager(QtWidgets.QWidget):
	recieptOpened = QtCore.Signal()
	recieptUpdated = QtCore.Signal()
	taxUpdated = QtCore.Signal()
	itemUpdated = QtCore.Signal(str)
	def __init__(self):
		super(RecieptBuddy_RecieptManager,self).__init__()
		self.rootItems = {}
		self.taxRate = 9.5
		self.recieptItems = []
		self.currentItem = None
		self.lastBackup = datetime.datetime.now()

		# data
		self.RecieptDir = os.path.join(os.environ.get('ArletaHouse'),'tools','recieptBuddy','source','lib','reciepts')
		if not os.path.isdir(self.RecieptDir):
			os.makedirs(self.RecieptDir)

		# widget creation
		self.uiRecieptSelector = QtWidgets.QComboBox()
		self.uiPayTo = QtWidgets.QComboBox()
		self.uiTaxRate = QtWidgets.QDoubleSpinBox()
		self.uiGroceryTreeWidget = QtWidgets.QTreeWidget()
		self.uiTemplateGroup = QtWidgets.QGroupBox('Item Template')
		self.uiItemTemplate = GroceryItemWidget()
		self.uiAddItem = QtWidgets.QPushButton(StyleUtils.getIcon('add'),'Add Item')

		# widget settings
		self.uiTaxRate.setValue(9.5)
		self.uiTemplateGroup.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))
		self.uiGroceryTreeWidget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
		for k in sorted(BillTo.keys()):
			self.uiPayTo.addItem(BillTo[k])
		self.uiAddItem.setEnabled(False)
		self.uiGroceryTreeWidget.setHeaderLabels(['Item Name', 'Item Price','CRV','Taxable','Tax','Subtotal','Bill To'])
		self.uiGroceryTreeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.uiGroceryTreeWidget.customContextMenuRequested.connect(self.groceryTreeMenuRequested)

		#Layout Construction
		self.layMain = QtWidgets.QVBoxLayout()
		self.layForm = QtWidgets.QFormLayout()
		self.layTemplate = QtWidgets.QVBoxLayout()
		self.layOperators = QtWidgets.QHBoxLayout()

		#layout settings
		self.layTemplate.addWidget(self.uiItemTemplate)
		self.layTemplate.addLayout(self.layOperators)

		self.layOperators.addStretch()
		self.layOperators.addWidget(self.uiAddItem)

		self.layForm.addRow('Reciept:',self.uiRecieptSelector)
		self.layForm.addRow('Pay To:',self.uiPayTo)
		self.layForm.addRow('Tax Rate:',self.uiTaxRate)
		# self.layForm.addRow('Items:',self.uiGroceryTreeWidget)

		self.layMain.addLayout(self.layForm)
		self.layMain.addWidget(self.uiGroceryTreeWidget)
		self.layMain.addWidget(self.uiTemplateGroup)

		# layout application
		self.setLayout(self.layMain)
		self.uiTemplateGroup.setLayout(self.layTemplate)

		self.uiItemTemplate.itemUpdated.connect(self.verifyTemplate)
		self.uiAddItem.clicked.connect(self.addItem)
		self.uiRecieptSelector.currentIndexChanged.connect(self.openReciept)
		self.uiTaxRate.valueChanged.connect(self.updateTaxRate)
		self.uiTaxRate.valueChanged.connect(self.updateRecieptFile)
		self.uiPayTo.currentIndexChanged.connect(self.updateRecieptFile)
		self.recieptUpdated.connect(self.updateRecieptFile)

		self.populateReciepts()

	def groceryTreeMenuRequested(self,point):
		treeItem = self.uiGroceryTreeWidget.itemAt(point)

		if treeItem is None:
			return None

		if treeItem.text(1) == '':
			return None

		self.currentItem = treeItem

		menu = QtWidgets.QMenu(parent = self)

		actEditItem = QtWidgets.QAction('Edit Item',self)
		actRemoveItem = QtWidgets.QAction('Remove Item',self)
		actAddNote = QtWidgets.QAction('View/Edit Note',self)
		actClearNotes = QtWidgets.QAction('Clear Notes',self)

		menu.addAction(actEditItem)
		menu.addAction(actRemoveItem)
		menu.addSeparator()
		menu.addAction(actAddNote)
		menu.addAction(actClearNotes)

		actRemoveItem.triggered.connect(self.removeItem)
		actEditItem.triggered.connect(self.editItem)
		actAddNote.triggered.connect(self.addNoteToCurrentItem)
		actClearNotes.triggered.connect(self.clearCurrentItemNotes)

		menu.exec_(self.uiGroceryTreeWidget.mapToGlobal(point))


	def updateTaxRate(self):
		self.taxRate = self.uiTaxRate.value()
		self.taxUpdated.emit()


	def openReciept(self):
		self.currentReciept = os.path.join(self.RecieptDir,self.uiRecieptSelector.currentText())
		self.rootItems = {}
		self.uiGroceryTreeWidget.clear()
		self.recieptItems = []

		if self.uiRecieptSelector.currentText() == 'New Reciept':
			creator = RecieptCreator(self.RecieptDir, parent = self)
			creator.createClicked.connect(self.createNewReciept)
			creator.exec_()

		elif self.uiRecieptSelector.currentText() == '':
			self.uiTemplateGroup.setEnabled(False)
			self.currentReciept = None
			self.uiTaxRate.setEnabled(False)
			self.uiPayTo.setEnabled(False)


		else:
			self.uiTemplateGroup.setEnabled(True)
			self.uiTaxRate.setEnabled(True)
			self.uiPayTo.setEnabled(True)			

			with open(self.currentReciept,'r') as jFile:
				data = json.load(jFile)

			for listItem in data['items']:
				self.addItem(itemData = listItem)

			self.uiTaxRate.setValue(float(data['taxRate']))
			self.taxRate = float(data['taxRate'])
			self.uiPayTo.setCurrentIndex(self.uiPayTo.findText(data['payableTo']))

		self.recieptOpened.emit()




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
		filteredFiles = []
		for file in files:
			if '.reciept' in file:
				filteredFiles.append(file)

		filteredFiles.sort()
		filteredFiles.reverse()

		self.uiRecieptSelector.addItem('')
		self.uiRecieptSelector.addItems(filteredFiles)
		self.uiRecieptSelector.addItem('New Reciept')


	def verifyTemplate(self):
		data = self.uiItemTemplate.getData()

		valid = True
		for k in data.keys():
			if k != 'itemNote':
				if data[k] == '':
					valid = False

		self.uiAddItem.setEnabled(valid)


	def clearCurrentItemNotes(self):
		self.currentItem.setNote('')
		self.updateRecieptFile()


	def addNoteToCurrentItem(self):
		noteEditor = NoteEditor(noteData = self.currentItem.itemData['itemNote'], parent = self)
		noteEditor.exec_()


	def setNote(self,note):
		self.currentItem.setNote(note)
		self.updateRecieptFile()


	def editItem(self):
		if self.currentItem is None:
			return None

		print self.currentItem.itemData
		uiItemEditor = ItemEditorDialog(listItem = self.currentItem, parent = self)
		uiItemEditor.exec_()


	def removeItem(self,listItem = None):
		if listItem is not None:
			item = listItem
		else:
			item = self.currentItem

		if item is not None:
			item.parent().removeChild(item)

		for i in range(len(self.recieptItems)):
			if self.recieptItems[i].text(1) != '':
				if self.recieptItems[i].itemData == item.itemData:
					self.recieptItems.pop(i)
					break


		self.updateRecieptFile()


	def addItem(self, itemData = None):
		if itemData is None:
			itemData = self.uiItemTemplate.getData()

		itemTotal = float(itemData['itemPrice']) + float(itemData['itemCrv']) + (float(itemData['itemPrice'])*self.taxRate)
		itemData['itemTotal'] = itemTotal

		if itemData['billTo'] not in self.rootItems.keys():
			self.createRootItem(itemData['billTo'])
			newItem = GroceryTreeItem(self.rootItems[itemData['billTo']],itemData = itemData, parentWidget = self)	
			self.uiGroceryTreeWidget.setItemSelected(newItem,True)
			self.recieptItems.append(newItem)		

		else:
			newItem = GroceryTreeItem(self.rootItems[itemData['billTo']],itemData = itemData, parentWidget = self)
			self.uiGroceryTreeWidget.setItemSelected(newItem,True)
			self.recieptItems.append(newItem)		

		self.uiItemTemplate.clear()
		self.recieptUpdated.emit()

	
	def updateRecieptFile(self):
		self.currentReciept = os.path.join(self.RecieptDir,self.uiRecieptSelector.currentText())

		with open(self.currentReciept,'r') as jFile:
			currentRecieptData = json.load(jFile)

		itemList = []
		for item in self.recieptItems:
			itemData = {}
			itemData['itemName'] = item.text(0)
			itemData['itemPrice'] = item.text(1)
			itemData['itemCrv'] = item.text(2)
			itemData['itemTaxable'] = item.text(3)
			if itemData['itemTaxable'] == 'True':
				itemData['tax'] = item.text(4)
				itemData['itemTotal'] = str((float(itemData['itemPrice']) + float(itemData['itemCrv'])) * (1 + self.taxRate/100))
			else:
				itemData['tax'] = '0'
				itemData['itemTotal'] = str(float(itemData['itemPrice']) + float(itemData['itemCrv']))

			itemData['billTo'] = item.text(6)
			itemData['itemNote'] = item.itemData['itemNote']

			itemList.append(itemData)

		currentRecieptData['items'] = itemList
		currentRecieptData['taxRate'] = self.uiTaxRate.value()
		currentRecieptData['payableTo'] = self.uiPayTo.currentText()

		self.createRecieptBackup()

		with open(self.currentReciept,'w') as jFile:
			json.dump(currentRecieptData, jFile, ensure_ascii=False, indent=4)


	def createRootItem(self,itemName):
		newTreeRoot = QtWidgets.QTreeWidgetItem(self.uiGroceryTreeWidget,[itemName])
		self.rootItems[itemName] = newTreeRoot


	def createRecieptBackup(self, force = False):
		makeBackup = True

		t = os.path.getmtime(self.currentReciept)
		recieptDateTime = datetime.datetime.fromtimestamp(t)
		
		if (datetime.datetime.now() - self.lastBackup).seconds < 120:
			makeBackup = False

		print 'Time Since Backup: {}'.format(str((datetime.datetime.now() - self.lastBackup).seconds))

		if force:
			makeBackup = True

		if makeBackup:
			self.lastBackup = datetime.datetime.now()
			fileBackupDir = os.path.join(self.RecieptDir,'_bak')
			if not os.path.isdir(fileBackupDir):
				os.makedirs(fileBackupDir)

			# iterator = 0
			# for file in os.listdir(fileBackupDir):
			# 	fileIterator = file.split('.')[0].split('_')[-1]
			# 	if fileIterator.isdigit():
			# 		if int(fileIterator) >= iterator:
			# 			iterator = int(fileIterator) + 1
			# 			if iterator > 10:
			# 				iterator = 0

			newestBackupTime = 10000
			newestFile = None
			for file in os.listdir(fileBackupDir):
				if file.split('.')[0].split('_')[-1].isdigit():
					fileEditTime = os.path.getmtime(os.path.join(fileBackupDir,file))
					fileDateTime = datetime.datetime.fromtimestamp(fileEditTime)

					fileAge = (datetime.datetime.now() - fileDateTime).seconds

					if fileAge < newestBackupTime:
						newestBackupTime = fileAge
						newestFile = file

			if newestFile is None:
				backupVersion = 0
			else:
				backupVersion = int(newestFile.split('.')[0].split('_')[-1]) + 1
				if backupVersion > 10:
					backupVersion = 0

			backupName = os.path.basename(self.currentReciept).split('.')[0] + '_bak_{}'.format('%02d' % backupVersion)
			backupFile = os.path.join(fileBackupDir,backupName + '.reciept')
			
			print 'Making Backup: {}'.format(backupName) 
			
			copyfile(self.currentReciept,backupFile)

		


class RecieptBuddy_BillPreview(QtWidgets.QWidget):
	def __init__(self):
		super(RecieptBuddy_BillPreview,self).__init__()
		self.fileWatcher = QtCore.QFileSystemWatcher()

		self.recieptParser = RecieptParser.Parser()

		self.uiScrollArea = QtWidgets.QScrollArea()
		self.lblBill = QtWidgets.QLabel()
		self.uiItemized = QtWidgets.QCheckBox('Itemized')

		# widget settings
		self.uiScrollArea.setWidgetResizable(True)

		self.layMain = QtWidgets.QVBoxLayout()
		self.layBillGroup = QtWidgets.QVBoxLayout()

		self.layMain.addWidget(self.uiScrollArea)
		self.layMain.addWidget(self.uiItemized)

		self.uiScrollArea.setWidget(self.lblBill)
		self.setLayout(self.layMain)

		self.uiItemized.stateChanged.connect(self.toggleItimized)

		self.fileWatcher.fileChanged.connect(self.updatePreview)


	def clear(self):
		self.fileWatcher.removePaths(self.fileWatcher.files())
		self.lblBill.setText('')
		self.recieptParser.clear()


	def toggleItimized(self):
		self.html = self.recieptParser.generateBill(itemized  = self.uiItemized.isChecked())
		self.lblBill.setText(self.html)


	def setReciept(self, reciept):
		self.reciept = reciept
		self.fileWatcher.addPath(reciept)
		self.updatePreview()


	def updatePreview(self):
		self.recieptParser.setReciept(self.reciept)
		self.html = self.recieptParser.generateBill(itemized = self.uiItemized.isChecked())
		self.lblBill.setText(self.html)



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
		self.uiItemList = RecieptBuddy_RecieptManager()
		self.uiBillPreview = RecieptBuddy_BillPreview()
		self.uiExportBill = QtWidgets.QPushButton('Export Bill')

		# widgetSettings
		self.uiSplitter.setOrientation(QtCore.Qt.Vertical)
		self.uiSplitter.addWidget(self.uiItemList)
		self.uiSplitter.addWidget(self.uiBillPreview)
		self.uiSplitter.setStyleSheet("QSplitter::handle{background: rgb(42, 42, 42);}")
		self.uiSplitter.setHandleWidth(12)
		self.uiExportBill.setEnabled(False)

		# LayoutGeneration
		self.layMain = QtWidgets.QVBoxLayout()
		self.layOperators = QtWidgets.QHBoxLayout()

		# Layout settings
		self.layMain.addWidget(self.uiSplitter)
		self.layMain.addLayout(self.layOperators)

		self.layOperators.addStretch()
		self.layOperators.addWidget(self.uiExportBill)

		# Layout Assignment
		self.uiCentralWidget.setLayout(self.layMain)

		self.setCentralWidget(self.uiCentralWidget)

		self.uiItemList.recieptOpened.connect(self.recieptUpdated)
		self.uiExportBill.clicked.connect(self.exportHTML)
		# self.uiItemList.recieptUpdated.connect(self.recieptUpdated)


	def recieptUpdated(self):
		reciept = self.uiItemList.currentReciept

		if reciept is None:
			self.uiExportBill.setEnabled(False)
			self.uiBillPreview.clear()

		else:
			if os.path.isfile(reciept):
				self.uiExportBill.setEnabled(True)
				self.uiBillPreview.setReciept(reciept)

	def exportHTML(self):
		exportDir = os.path.dirname(self.uiItemList.currentReciept)
		destFile = os.path.join(exportDir,'invoice.html')

		file1 = open(destFile, "w")

		file1.writelines(self.uiBillPreview.html)

		file1.close()

		os.startfile(destFile)



class RecieptBuddy(RecieptBuddy_UI):
	def __init__(self):
		super(RecieptBuddy,self).__init__()



################################################################################
# Unit Testing
################################################################################
def unitTest_SpinBox():
	app = QtWidgets.QApplication(sys.argv)


	testDialog = QtWidgets.QDialog()
	layTest = QtWidgets.QHBoxLayout()
	layTest.addWidget(MoneySpinner())
	testDialog.setLayout(layTest)

	ex = testDialog
	StyleUtils.setStyleSheet(ex)
	ex.show()
	sys.exit(app.exec_())


def unitTest_Main():
    app = QtWidgets.QApplication(sys.argv)
    ex = RecieptBuddy()
    StyleUtils.setStyleSheet(ex)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
	unitTest_Main()
	# unitTest_SpinBox()