import string, os
import MySQLdb
from SimpleTableAdapter import SimpleTableAdapter

import gettext
gettext.install('ForestMan')

class UnitList(SimpleTableAdapter):
	"""
	Middleware object representing the user modifiable list of possible units
	"""
	def __init__(self, databaseconnection):
		"""Initialise UnitList. Takes a DB-API Connection object"""
		import TableConstructors
		SimpleTableAdapter.__init__(self,databaseconnection,TableConstructors.createUnits)		
		

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
		conn.cursor().execute("DROP TABLE IF EXISTS Units"); 
		list=UnitList(conn) 
		list.add( {'Name':'Monkeys'});
		list.add( {'Name':'baboons'});
		print list.get()
		
		item=list.get()[1];
		item['Name']='Baboons'
		list.modify(item);
		print list.get()

		list.delete(item);
		print list.get()

	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
