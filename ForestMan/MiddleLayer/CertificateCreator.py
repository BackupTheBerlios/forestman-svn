import string
import time
import MySQLdb

import gettext
gettext.install('ForestMan')

from Globals import TAX_MULTIPLIER, TAX_RATE

class CertificateCreator:
	"""
  	Middleware object representing the list of uncertified processes per Purchase Order
	"""
	def __init__(self, databaseconnection,purchaseorder):
		"""Initialise CertificateCreator. Takes a DB-API Connection object and a purchase order number"""
		self.databaseconnection=databaseconnection
		self.cursor=self.databaseconnection.cursor(MySQLdb.cursors.DictCursor);
		self.purchaseorder=purchaseorder
		import TableConstructors
		TableConstructors.createContractedItems(self.cursor)
		TableConstructors.createContractedTransactions(self.cursor)
		TableConstructors.createCertificates(self.cursor)
		#self.selection is a list of ContractedTransactionId of the items that will be certified	
		self.selection=[]
		
	def get(self):
		"""
		Returns a list of Contractor, Task, Contracted Qty, Contracted UnitPrice,
		Accumulated qty,  Remaining qty and total price for each uncertified contract transaction
		for the current purchaseorder
		"""
		self.cursor.execute("""
							SELECT
								ContractedTransactions.*,
								PurchaseOrderList.ContractorId,
								ContractedItems.ContractedQty
							FROM ContractedTransactions
							LEFT JOIN Certificates ON
							ContractedTransactions.ContractedTransactionId = Certificates.ContractedTransactionId
							LEFT JOIN ContractedItems ON
							ContractedTransactions.ContractedItemId = ContractedItems.ContractedItemId
							LEFT JOIN PurchaseOrderList
							ON ContractedItems.PurchaseOrder = PurchaseOrderList.PurchaseOrder
							WHERE
							Certificates.ContractedTransactionId IS NULL AND
							ContractedItems.PurchaseOrder = %s""",self.purchaseorder)
		uncerttrans=self.cursor.fetchall()
		for i in uncerttrans:
			self.cursor.execute(
				"""	
				SELECT
					SUM(ContractedTransactions.QtyCompleted) AS AccUncertQty,
					SUM(ContractedTransactions.QtyCompleted * ContractedTransactions.UnitPrice) AS TotalPrice,
					SUM(ContractedTransactions.QtyCompleted * ContractedTransactions.UnitPrice) * """
				+ str(TAX_MULTIPLIER) + """ AS PriceIncTax
				FROM ContractedTransactions
				LEFT JOIN Certificates ON
				ContractedTransactions.ContractedTransactionId = Certificates.ContractedTransactionId
				WHERE
				Certificates.ContractedTransactionId IS NULL AND
				ContractedTransactions.ContractedItemId=%(ContractedItemId)s AND
				ContractedTransactions.ContractedTransactionId <= %(ContractedTransactionId)s
				GROUP BY ContractedTransactions.ContractedItemId
				""", i)
			calc=self.cursor.fetchone()
			if calc:
				i.update(calc)
			self.cursor.execute(
				"""	
				SELECT ContractedItems.ContractedQty - SUM(QtyCompleted) AS RemainingQty
				FROM ContractedTransactions
				LEFT JOIN ContractedItems ON
				ContractedTransactions.ContractedItemId = ContractedItems.ContractedItemId
				WHERE
				ContractedTransactions.ContractedItemId=%(ContractedItemId)s AND
				ContractedTransactions.ContractedTransactionId <= %(ContractedTransactionId)s
				GROUP BY ContractedTransactions.ContractedItemId
				""", i)
			calc=self.cursor.fetchone()
			if calc:
				i.update(calc)
			if i['ContractedTransactionId'] in self.selection:
				i['Selected']=True
			else:
				i['Selected']=False
		return uncerttrans
	
	def modify(self, fields ):
		"""
		fields is a dict that may contain 'QtyCompleted' or'UnitPrice'. 
		Must contain a ContractedTransactionId
		"""
		assert(fields.has_key('ContractedTransactionId'))

		s = "UPDATE ContractedTransactions SET "
		addcomma=False;
		for name in	 fields:
			if name in ('QtyCompleted','UnitPrice'):
				if addcomma:
					s+=", "
				s+=name + " = %("+name+")s "
				addcomma=True
			
		s+="WHERE ContractedTransactionId = %(ContractedTransactionId)s"

		self.cursor.execute(s,fields)
	
	def select(self,selected):
		"""
		select a given 'ContractedTransactionId'
		"""
		if (selected not in self.selection):
			self.selection.append(selected)

	def deselect(self,selected):
		"""
		deselect a given 'ContractedTransactionId'
		"""
		if selected in self.selection:
			self.selection.remove(selected)
			assert(selected not in self.selection)

class CertificateMaker:
	"""class to preview certificates, generate pdf for them, and store in the database"""
	def __init__(self, databaseconnection, certificatecreator):
		"""
		Create a CertificateMaker. takes a databaseconnection and a CertificateCreator.
		The selection and logic of the passed CertificateCreator is used when making certifcates
		"""
		self.databaseconnection=databaseconnection
		self.cursor=self.databaseconnection.cursor(MySQLdb.cursors.DictCursor);
		self.certificatecreator=certificatecreator
		import TableConstructors
		TableConstructors.createCertificates(self.cursor)

	def previewcertificate(self):
		#returns a dict with fields CertificateNumber, PurchaseOrder,MonthYear,TaskTable,Tax, GrandTotal,
		#Contractor, WorkInspector, AreaHead, Date
		#TaskTable is a list of dicts, giving a table of Task, StandId,Quantity,Unit, UnitPrice,TotalPrice,
		#RunningTotal and RemainingQuantity
		ret={}
		self.cursor.execute("SELECT MAX(CertificateId)+1 FROM Certificates")	
		ret['CertificateNumber']=self.cursor.fetchone()['MAX(CertificateId)+1']
		if ret['CertificateNumber'] == None:
			ret['CertificateNumber']=0
		ret['PurchaseOrder']=self.certificatecreator.purchaseorder
		ret['MonthYear']=time.strftime("%B %y")

		if self.certificatecreator.selection:
			lst=""
			addcomma=False
			for i in self.certificatecreator.selection:
				if addcomma:
					lst+=", "
				lst+=str(i)
				addcomma=True
			self.cursor.execute("""
							SELECT
							  ContractedItems.ContractedItemId, 
							  TaskList.Description as Task,
							  PlanningItems.StandId,
							  SUM(ContractedTransactions.QtyCompleted) AS Quantity,
							  Units.Name AS Unit,
							  MAX(ContractedTransactions.UnitPrice) AS UnitPrice,
							  SUM(ContractedTransactions.UnitPrice * ContractedTransactions.QtyCompleted) AS TotalPrice
							FROM ContractedTransactions
							LEFT JOIN ContractedItems
							ON ContractedItems.ContractedItemId = ContractedTransactions.ContractedItemId
							LEFT JOIN Units
							ON ContractedItems.ContractedUnitId = Units.UnitId
							LEFT JOIN PlanningItems
							ON ContractedItems.PlanningItemId = PlanningItems.PlanningItemId
							LEFT JOIN TaskList
							ON PlanningItems.TaskId = TaskList.TaskId
							WHERE ContractedTransactionId IN ("""+lst+""")
							GROUP BY ContractedItems.ContractedItemId		
						""")
			tasktable=self.cursor.fetchall()

			for i in tasktable:
				self.cursor.execute("""
					SELECT
					  SUM(QtyCompleted) AS RunningTotal,
					  ContractedItems.ContractedQty - SUM(QtyCompleted) AS RemainingQty
					FROM ContractedTransactions
					LEFT JOIN ContractedItems ON
					ContractedTransactions.ContractedItemId = ContractedItems.ContractedItemId
					WHERE
					ContractedTransactions.ContractedItemId=%(ContractedItemId)s
					GROUP BY ContractedTransactions.ContractedItemId
					""",i)
				i.update(self.cursor.fetchone())

			ret['TaskTable']=tasktable
			total=0
			for i in tasktable:
				total+=i['TotalPrice']
			ret['Tax']=total*TAX_RATE/100
			ret['GrandTotal']=total+ret['Tax']

		else:
			ret['TaskTable']=None
			ret['Tax']=0
			ret['GrandTotal']=0
		return ret
		
	def generatecertificate(self):
		#TODO: actually create pdf
		#for now just certify the buggers =)
		sql="INSERT INTO Certificates (ContractedTransactionId) VALUES "
		addcomma=False
		for i in self.certificatecreator.selection:
			if addcomma:
				sql+=", "
			sql+="("+str(i)+")"
			addcomma=True
			
		self.cursor.execute(sql)
																						   
		
if __name__ == "__main__":
	import sys
	try:
		conn = MySQLdb.connect (host = "localhost",
								user = "test",
								db = "test")
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	try:
		conn.cursor().execute("DROP TABLE IF EXISTS PlanningItems"); 
	
	except MySQLdb.Error, e:
	        print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
