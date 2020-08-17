import os,sys,json, pprint


GroupHeader = '''
<h1>{}: {}</h1>
<h2>Payable To: {}</h2>
<h3>Total: ${}</h3>
<ul>
'''

GroupLineItem = '''
<li>{}: ${}</li>
'''

PurchaseLineItem = '''
<ul>
<li>"{}" -- <strong>Price</strong>: ${} | <strong>CRV</strong>:${} | <strong>Tax</strong>: ${} | <strong>Subtotal</strong>: ${}</li>
</ul>
'''

class Parser(object):
	def __init__(self):
		self.recieptData = None
		

	def clear(self):
		self.recieptData = None
		self.groupBillHTML = ''
		self.GroupBill = {}


	def setReciept(self, jsonFile):
		with open(jsonFile, 'r') as jFile:
			data = json.load(jFile)
		
		self.recieptData = data


	def generateBill(self, itemized = False):
		if self.recieptData is None:
			return None

		self.groupBillHTML = ''
		self.GroupBill = {}

		for listItem in self.recieptData['items']:
			if listItem['billTo'] not in self.GroupBill.keys():
				template = {}

				template['total'] = 0
				template['items'] = []

				self.GroupBill[listItem['billTo']] = template

		grandTotal = 0
		for listItem in self.recieptData['items']:
			grandTotal += float(listItem['itemTotal'])

			self.GroupBill[listItem['billTo']]['items'].append(listItem)
			self.GroupBill[listItem['billTo']]['total'] += float(listItem['itemTotal'])


		self.groupBillHTML += GroupHeader.format(
				self.recieptData['storeName'],
				self.recieptData['date'],
				self.recieptData['payableTo'],
				str(round(grandTotal,2))
			)

		for k in sorted(self.GroupBill.keys()):
			self.groupBillHTML += GroupLineItem.format(k,self.GroupBill[k]['total'])
			if itemized:
				for item in self.GroupBill[k]['items']:
					self.groupBillHTML += PurchaseLineItem.format(
							item['itemName'],
							round(float(item['itemPrice']),2),
							round(float(item['itemCrv']),2),
							round(float(item['tax']),2),
							round(float(item['itemTotal']),2)
						)

		return self.groupBillHTML


################################################################################
# Unit Testing
################################################################################
def unitTest_setReciept():
	filepath = 'Z:/projects/repos/ArletaHouse/tools/RecieptBuddy/source/lib/reciepts/8-16-2020_ralphs.reciept'

	parser = Parser()
	parser.setReciept(filepath)


def unitTest_groupBill():
	filepath = 'Z:/projects/repos/ArletaHouse/tools/RecieptBuddy/source/lib/reciepts/8-16-2020_ralphs.reciept'

	parser = Parser()
	parser.setReciept(filepath)	
	print parser.generateBill(itemized = True)


if __name__ == '__main__':
	# unitTest_setReciept()
	unitTest_groupBill()