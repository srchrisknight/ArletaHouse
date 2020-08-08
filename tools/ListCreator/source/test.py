import os,sys,csv,pprint

sys.path.append(os.environ.get('PS_SITEPACKAGES'))

from Qt import QtWidgets, QtCore, QtGui

from PictureShop2.Shared import StyleUtils

csvfilepath = r'C:\Users\Chris\Downloads\Shopping Template 7-13-2020 - Eric_Bre.csv'

# with open(csvfilepath) as csv_file:
# 	csv_reader = csv.reader(csv_file, delimiter = ',')
# 	line_count = 0
# 	for row in csv_reader:
# 		if line_count == 0:
# 			sheetName = row[0]
# 			print sheetName

# 		line_count += 1

groupInitials = {
	'Eric/Bre':'EK/BT',
	'Jesse':'JK',
	'Chris Mona Denise':'CMD',
	'Brad':'BK',
	'Nancy':'NS',			
}


class GroceryListGenerator(QtWidgets.QDialog):
	def __init__(self):
		super(GroceryListGenerator,self).__init__()
		self.setWindowTitle('Grocery List Generator')
		self.resize(300,50)

		self.lblSource = QtWidgets.QLabel('Source:')
		self.uiFolderDrop = QtWidgets.QComboBox()
		self.uiCreateButton = QtWidgets.QPushButton('Create/Update List')

		self.laySource = QtWidgets.QHBoxLayout()
		self.layOperators = QtWidgets.QHBoxLayout()
		self.layMain = QtWidgets.QVBoxLayout()

		self.laySource.addWidget(self.lblSource)
		self.laySource.addWidget(self.uiFolderDrop)

		self.layOperators.addStretch()
		self.layOperators.addWidget(self.uiCreateButton)

		self.layMain.addLayout(self.laySource)
		self.layMain.addLayout(self.layOperators)

		self.setLayout(self.layMain)

		self.listDates()

		self.uiCreateButton.clicked.connect(self.createList)

	def listDates(self):
		self.datesDir = r'Z:\projects\python\tools\GroceryCompiler\lib'

		for date in os.listdir(self.datesDir):
			self.uiFolderDrop.addItem(date)


	def createList(self):
		groceryList = {}
		csvDir = os.path.join(self.datesDir,self.uiFolderDrop.currentText())

		for file in os.listdir(csvDir):
			csvfilepath = os.path.join(csvDir,file)
			with open(csvfilepath) as csv_file:
				csv_reader = csv.reader(csv_file, delimiter = ',')
				line_count = 0
				catagory = None

				for row in csv_reader:
					if line_count == 0:
						sheetName = row[0]

					if '#' in row[0]:
						catagory = row[0].replace('#','')

						if catagory not in groceryList.keys():
							groceryList[catagory] = []
					else:
						if catagory is not None:
							if row[0] != '':
								item = {}

								item['name'] = row[0]
								item['quantity'] = row[1]
								item['desc'] = row[2]

								if row[3] == '':
									item['alt'] = 'None'
								else:
									item['alt'] = row[3]

								if row[4] == '':
									item['initials'] = groupInitials[sheetName]
								else:
									item['initials'] = row[4]


								groceryList[catagory].append(item)

					line_count += 1

		self.createHtml(groceryList)

	def createHtml(self,groceryList):
		html = ''
		catagoryTemplate = '<h3>{}</h3>'
		itemTemplate = '<p>&#9634 <strong>{}:&nbsp;</strong>[{}] | alt = {} -- <em>{}</em></p>'

		for key in sorted(groceryList.keys()):
			if len(groceryList[key]) > 0:
				html += catagoryTemplate.format(key)

				for item in groceryList[key]:
					html += itemTemplate.format(item['name'], item['quantity'], item['alt'], item['initials'])

				html +='<br><br>'

		print html

		# pprint.pprint(groceryList)



def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = GroceryListGenerator()
    StyleUtils.setStyleSheet(ex)
    ex.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
	main()