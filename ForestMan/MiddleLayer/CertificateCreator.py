import string, os
import MySQLdb

import gettext
gettext.install('ForestMan')

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
		
		
	def get(self):
		"""
		Returns the PlanningList as a dictionary 
		"""
		self.cursor.execute("SELECT * FROM ContractedTransactions WHERE ")
		return self.cursor.fetchall()
	

	def modify(self, fields ):
		"""
		fields is a dict that may contain any valid key names from this object. 
		Must contain a PlanningItemId
		"""
		assert(fields.has_key('PlanningItemId'))

		s = "UPDATE PlanningItems SET "
		addcomma=False;
		for name in fields:
			if name != 'PlanningItemId':
				if addcomma:
					s+=", "
				s+=name + " = %("+name+")s "
				addcomma=True
			
		s+="WHERE PlanningItemId = %(PlanningItemId)s"

		self.cursor.execute(s,fields)
	


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
		list=PlanningList(conn) 
		list.add( {'BudgetYear':1978, 'PropId': 1234, 'StandId':2345, 'Quantity':12000, 'Unit':'tonnes', 'TaskId':3456});
		print list.get()
		item=list.get()[0];
		item['BudgetYear']=1976
		item['PropId']=12000
		item['YieldFac']=2.6
		item['EstPrice']=2307.50

		list.modify(item);
		print list.get()
		list.delete(item);
		print list.get()
	except MySQLdb.Error, e:
	        print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
