import string, os
import MySQLdb

from SimpleTableAdapter import SimpleTableAdapter

import gettext
gettext.install('ForestMan')

class ContractorCreator(SimpleTableAdapter):
	"""
	Middleware object representing the user modifiable list of possible contractors
	"""
	def __init__(self, databaseconnection):
		"""Initialise ContractorCreator. Takes a DB-API Connection object"""
		import TableConstructors
		SimpleTableAdapter.__init__(self, databaseconnection, TableConstructors.createContractors)
		
	def fillemptyfields(self,data):	
		self.fill(data,'Address',"")
		self.fill(data,'Location',"")
		self.fill(data,'CUIT',"")
		self.fill(data,'Phone',"")
		SimpleTableAdapter.fillemptyfields(self,data)
		

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
		conn.cursor().execute("DROP TABLE IF EXISTS Contractors"); 
		list=ContractorCreator(conn) 
		list.add( {'Name':'Dodgy Daves Contracting Co.'});
		list.add( {'Name':'Cunning Kevins Cutting Co.', 'Address':'Nowhere 100, Notown','Phone':'0800 696969'});
		print list.get()
		item=list.get()[0];
		item['Phone']='(11) 4948 4746'

		list.modify(item);
		print list.get()
		list.delete(item);
		print list.get()
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
