import string, os
import MySQLdb

import gettext
gettext.install('ForestMan')


class TransactionCreator:
	"""
  	Middleware object representing a list of uncerified ContractedTasks , filtered by TaskGroup,
	and additionally any one or more of PropertyId, StandId or PurchaseOrder, 
	which the user can then use to log a transaction in (partial) completion of one of these tasks.
	the instance variable 'filters' should be a dictionay whose keys are names of items to filter on,
	and the corresponding value being the filter
	Possible names are 'PropertyId','StandId','PurchaseOrder'
	e.g. {'PropertyId':3,'PurchaseOrder':3782}
	TODO

	"""
	def __init__(self, databaseconnection, taskgroup):
		"""Initialise PlanningList. Takes a DB-API Connection object"""
		self.databaseconnection=databaseconnection
		self.cursor=self.databaseconnection.cursor(MySQLdb.cursors.DictCursor);
		import TableConstructors
		TableConstructors.createContractedTransactions(self.cursor)
		TableConstructors.createContractedItems(self.cursor)
		TableConstructors.createCertificates(self.cursor)

		self.taskgroup=taskgroup
		self.filters={}
			

	def get(self):
		"""
		Returns the list of filtered transactions as a dictionary 
		TODO
		"""
		retlist=[];
		query="SELECT * FROM ContractedItems"
		if self.filters:
			query+=" WHERE "
		addcomma=False;
		for i in self.filters:
			if addcomma:
				query+=", "
			query+=i+" = "+str(self.filters[i])
			addcomma=True
			
		self.cursor.execute(query)
		contrans=self.cursor.fetchall()
		for i in contrans:
			if i['Completed']=='N':	
				#user has marked this item as unfinished,
				#its something we should list. return it, adding a list of all current transactions
				self.cursor.select("SELECT * FROM ContractedTransactions "
						   "WHERE ContractedItemId = %(ContractedItemId)s",
						   i)
				i['Transactions']=self.cursor.fetchall()
				total=0
				for j in i['Transactions']:
					total+=j['QtyCompleted']
				i['RunningTotal']=total
				i['RemainingQty']=i['ContractedQty']-total
				retlist.append(i)
				
			#else i['Completed']=='Y':
				#user has marked this item as completed
				#ignore it
			
				
				
		return self.cursor.fetchall()

	def createtransaction(self, fields):
		""" Create a new transaction.
		Create a new transaction. fields should be a dict containing at least ContractedItemId,
		QtyCompleted and CompletionDate. It may optionally contain ContractedUnitPrice.
		"""
		assert(fields.has_key('ContractedItemId'))
		assert(fields.has_key('QtyCompleted'))
		assert(fields.has_key('CompletionDate'))

		def fillkey(keyname, columnname):
			if not fields.has_key(keyname):
				self.cursor.execute("SELECT "+columnname+" FROM ContractedItems WHERE "
				"ContractedItemId = %(ContractedItemId)s", fields)
				if self.cursor.rowcount > 0:
					fields[keyname]=self.cursor.fetchall()[0][columnname]
				else:
					fields[keyname]=None
		fillkey('ContractedUnitPrice', 'ContractedUnitPrice')
		self.cursor.execute("""
					INSERT INTO ContractedTransactions 
					(ContractedItemId, QtyCompleted, CompletionDate, ContractedUnitPrice)
					VALUES 
					(%(ContractedItemId)s, %(QtyCompleted)s, 
					 %(CompletionDate)s, %(ContractedUnitPrice)s)
				    """,fields)


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
		from PurchaseOrderList import PurchaseOrderList
		tc= TransactionCreator(conn, "Nursery")
		tc.createtransaction({'ContractedItemId':1, 'QtyCompleted':12, 'CompletionDate':30-12-2004, 'PurchaseOrder':1234})
		tc.createtransaction({'ContractedItemId':2, 'QtyCompleted':34000, 'CompletionDate':30-1-2003, 'PurchaseOrder':1234})
		tc.createtransaction({'ContractedItemId':3, 'QtyCompleted':237, 'CompletionDate':30-12-2005, 'PurchaseOrder':3456})
		tc.createtransaction({'ContractedItemId':4, 'QtyCompleted':786, 'CompletionDate':02-12-2004, 'ContractedUnitPrice':12.99, 'PurchaseOrder':5678})
		print tc.get()
		tc.filters={'PurchaseOrder':1234}
		print tc.get()
		
	except MySQLdb.Error, e:
	        print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
