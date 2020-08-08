import os,sys,csv,pprint, webbrowser

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
	'Chris/Mona/Denise':'CMD',
	'Brad':'BK',
	'Nancy':'NS',
	'Family':'F'			
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
		self.mealList = {}
		self.csvDir = os.path.join(self.datesDir,self.uiFolderDrop.currentText())

		for file in os.listdir(self.csvDir):
			print file
			csvfilepath = os.path.join(self.csvDir,file)
			with open(csvfilepath) as csv_file:
				csv_reader = csv.reader(csv_file, delimiter = ',')
				line_count = 0

				if 'meal plan' in file.lower():
					mealPlan = file.split('.')[0].split(' - ')[-1]
					self.mealList[mealPlan] = {}
					for row in csv_reader:
						if line_count > 0:
							if row[1] != '':
								self.mealList[mealPlan][str(line_count)] = {'name':row[1],'ingrediants':[], 'day':row[0], 'date':row[4], 'chef':row[2], 'sousChef':row[3]}		
						line_count += 1

		for file in os.listdir(self.csvDir):
			if '.html' in file:
				# print file
				continue
			# print file
			csvfilepath = os.path.join(self.csvDir,file)
			with open(csvfilepath) as csv_file:
				# print csvfilepath
				csv_reader = csv.reader(csv_file, delimiter = ',')
				line_count = 0

				if 'meal plan' in file.lower() or 'datalists' in file.lower():
					pass
				else:
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
									# print row
									item = {}

									item['name'] = row[0]
									item['quantity'] = row[1]

									if row[2] == '':
										item['desc'] = 'None'
									else:
										item['desc'] = row[2]

									if row[3] == '':
										item['alt'] = 'None'
									else:
										item['alt'] = row[3]

									if row[4] == '':
										item['initials'] = groupInitials[sheetName]
									else:
										item['initials'] = row[4]

									item['meal'] = row[5]
									if row[5] != '':
										self.placeItemInMeal(item)
										# for k in self.mealList.keys():
										# 	if row[5].lower() == k.lower():
										# 		self.mealList[k]['ingrediants'].append(
										# 			{
										# 				'name':item['name'],
										# 				'quantity':item['quantity']
										# 			}
										# 		)


									groceryList[catagory].append(item)

						line_count += 1
		print self.mealList
		self.createMealPlans(self.mealList)
		self.createGroceryList(groceryList)

	def placeItemInMeal(self,item):
		for k in self.mealList.keys():
			for index in self.mealList[k]:
				if self.mealList[k][index]['name'] == item['meal']:
					self.mealList[k][index]['ingrediants'].append({'name':item['name'],'quantity':item['quantity']})


	def createMealPlans(self,mealList):
		html = '''
<!DOCTYPE html>
<html>
<head>
<link href='https://fonts.googleapis.com/css?family=Amatic SC' rel='stylesheet'>
<style>
body {
    font-family: 'Amatic SC';font-size: 22px;
}
</style>
</head>
<body>'''
		recipeHTML = '<style>p.small { line-height: 0.2;}</style>'
		mealPlan = '<p class = "small"><h3>{}</h3></small>'
		mealRecipe = '<p class = "small"><h3>{}</h3></small>'
		dayTemplate = '<p>&#9634 <strong>{}:&nbsp;</strong>[{}] | {} -- {}/{}</p>'
		ingrediantItem = '<p class = "small"><small>&#9634 <strong>{}:&nbsp;</strong> -- {}</small></p>'

		for plan in mealList.keys():
			#add sorty mabob here
			html += mealPlan.format(plan)
			recipeHTML += '<h2>{}</h2>'.format(plan.split('.')[0].replace(' ',''))

			counter = 0		
			for index in sorted(mealList[plan].keys()):
				if counter == 7:				
					html += '<br>'
				daysData = mealList[plan][index]
				dayHTML = dayTemplate.format(daysData['day'],daysData['date'],daysData['name'], daysData['chef'], daysData['sousChef'])
				dayHTML = dayHTML.replace(' -- /','')
				if daysData['sousChef'] == '':
					dayHTML = dayHTML.replace('{}/'.format(daysData['chef']),'{}'.format(daysData['chef']))
				html += dayHTML

				recipeHTML += mealRecipe.format(mealList[plan][index]['name'])

				for ingrediant in mealList[plan][index]['ingrediants']:
					recipeHTML += ingrediantItem.format(ingrediant['name'],ingrediant['quantity'])
				counter += 1

				
			destFile = os.path.join(self.csvDir,'{}-Ingrediants.html'.format(plan.split('.')[0].replace(' ','')))
			file1 = open(destFile, "w")
			file1.writelines(recipeHTML)
			file1.close()
			os.startfile(destFile)
			print 'wtf'


			html += '''
</body>
</html>'''	
			# print html		
			destFile = os.path.join(self.csvDir,'{}.html'.format(plan.replace(' ','')))
			file1 = open(destFile, "w")
			file1.writelines(html)
			file1.close()
			os.startfile(destFile)





		# print '\n\n'

		# print html


	def createGroceryList(self,groceryList):
		html = '<style>p.small { line-height: 0.2;}</style>'
		catagoryTemplate = '<p class = "small"><h3>{}</h3></small>'
		itemTemplate = '<div class="no-break"><p class = "small"><small>&#9634 <strong>{}:&nbsp;</strong>[{}] | desc = <u>{}</u> | alt = <strong>{}</strong> -- <em>{}</em></small></p></div>'

		for key in sorted(groceryList.keys()):
			if len(groceryList[key]) > 0:
				html += catagoryTemplate.format(key)

				for item in groceryList[key]:
					html += itemTemplate.format(item['name'], item['quantity'], item['desc'], item['alt'], item['initials'])

				html +='<p class = "small"><br></small>'



		destFile = os.path.join(self.csvDir,'GroceryList.html')

		file1 = open(destFile, "w")

		file1.writelines(html)

		file1.close()

		os.startfile(destFile)



def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = GroceryListGenerator()
    StyleUtils.setStyleSheet(ex)
    ex.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
	main()