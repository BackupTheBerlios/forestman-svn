import string, os
import MySQLdb

import gettext
gettext.install('ForestMan')
from TransactionCreator import TransactionCreator

class HarvesterTransactionCreator(TransactionCreator):
	"""
	Middleware object representing a specialisation of TransactionCreator which adds
	extra data for use by the Harvestry manager
	"""

	def __init__(self, databaseconnection, taskgroupid):
		"""Initialise HarvesterTransactionCreator. Takes a DB-API Connection object and a task group id"""
		TransactionCreator.__init__(self,databaseconnection,taskgroupid)
		import TableConstructors
		TableConstructors.createInvoices(self.cursor)
		
	def get(self):
		"""
		gets contracted transactions as per superclass, and attaches relevent invoice information
		"""
		data=TransactionCreator.get(self)
		for i in data:
			for j in i['Transactions']:
				self.cursor.execute("SELECT * from Invoices WHERE ContractedTransactionId = %(ContractedTransactionId)s",j)
				j['Invoices']=self.cursor.fetchall()
		return data
				

	def createinvoice(self,data):
		"""
		Creates an invoice. data must have at least 'ContractedTransactionId'and InvoiceNo
		optional fields are ScaleTicketNo, PlateNo, Destination, NoOfLogs,
		LogLength, LogDiameterMin, LogDiameterMax
		"""
		assert(data.has_key('ContractedTransactionId'))
		assert(data.has_key('InvoiceNo'))

	
		query_top = "INSERT INTO Invoices ("
		query_bottom = ") VALUES ("

		addcomma=False;
		for i in data:
			if addcomma:
				query_top+=", "
				query_bottom+=", "
			query_top+=i
			query_bottom += "%("+i+")s"
			addcomma=True

		query=query_top+query_bottom+")"
		self.cursor.execute(query , data)

	def modifyinvoice(self,data):
		"""
		Modify an invoice. data should have at least 'InvoiceId' and not 'ContractedTransactionId'
		"""

		assert(data.has_key('InvoiceId'))

		s = "UPDATE Invoices SET "
		addcomma=False;
		for name in data:
			if name != self.fields[0]:
				if addcomma:
					s+=", "
				s+=name + " = %("+name+")s "
				addcomma=True
			
		s+="WHERE InvoiceId = %(InvoiceId)s"

		self.cursor.execute(s,data)
					
	def deleteinvoice(self,data):
		"""
		Delete invoice. data should have at least 'InvoiceId'
		"""
		assert (data.has_key('InvoiceId'))
		self.cursor.execute("DELETE FROM Invoices "+
							" WHERE InvoiceId = %(InvoiceId)s",id);

			
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
		conn.cursor().execute("DROP TABLE IF EXISTS ContractedTransactions"); 
		conn.cursor().execute("DROP TABLE IF EXISTS ContractedItems"); 
		conn.cursor().execute("DROP TABLE IF EXISTS Invoices"); 
		from PurchaseOrderList import PurchaseOrderList
		list=PurchaseOrderList(conn) 
		contract1=list.add({'PlanningItemId':1, 'PurchaseOrder':1234, 'ContractorId':23, 'StartDate':"3/4/89", 'EndDate':"3/4/99"});
		contract2=list.add({'PlanningItemId':2, 'PurchaseOrder':5477, 'ContractorId':23, 'StartDate':"3/4/89", 'EndDate':"3/4/99"});


		def ap(d,v):
			d.update(v)
			return d

		tc=HarvesterTransactionCreator(conn)
		trans1=tc.createtransaction(ap(contract1,{'QtyCompleted':12, 'CompletionDate':30-12-2004, 'PurchaseOrder':1234}))
		tc.createtransaction(ap(contract1,{'QtyCompleted':34000, 'CompletionDate':30-1-2003, 'PurchaseOrder':1234}))
		tc.createtransaction(ap(contract2,{'QtyCompleted':237, 'CompletionDate':30-12-2005, 'PurchaseOrder':3456}))
		tc.createtransaction(ap(contract2,{'QtyCompleted':786, 'CompletionDate':02-12-2004, 'ContractedUnitPrice':12.99, 'PurchaseOrder':5678}))
		print tc.get()

		trans1['InvoiceNo']=1234
		tc.createinvoice(newtrans)
		print tc.get()
		
	except MySQLdb.Error, e:
	        print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
