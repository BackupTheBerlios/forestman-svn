import string, os
import MySQLdb
from SimpleTableAdapter import SimpleTableAdapter

import gettext
gettext.install('ForestMan')

class TaskGroupCreator(SimpleTableAdapter):
	"""
	Middleware object representing the user modifiable list of possible taskgroups
	"""
	def __init__(self, databaseconnection):
		"""Initialise TaskGroupCreator. Takes a DB-API Connection object"""
		import TableConstructors
		SimpleTableAdapter.__init__(self,databaseconnection,TableConstructors.createTaskGroups)		
		

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
		conn.cursor().execute("DROP TABLE IF EXISTS TaskGroups"); 
		list=TaskGroupCreator(conn) 
		list.add( {'Name':'siliviculture'});
		list.add( {'Name':'Harvesting'});
		print list.get()
		
		item=list.get()[0];
		item['Name']='Silviculture'
		list.modify(item);
		print list.get()

		list.delete(item);
		print list.get()

	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
