import string, os
import MySQLdb
from SimpleTableAdapter import SimpleTableAdapter

import gettext
gettext.install('ForestMan')

class PlanningList(SimpleTableAdapter):
	"""
	Middleware object representing the user actionable list of planned tasks
	"""
	def __init__(self, databaseconnection):
		"""Initialise PlanningList. Takes a DB-API Connection object"""
		import TableConstructors
		SimpleTableAdapter.__init__(self,databaseconnection,TableConstructors.createPlanningItems)
				
	def fillemptyfields(self,data):	
		self.fill(data,'Quantity')
		self.fill(data,'YieldFac',1)
		self.fill(data,'EstPrice')
		self.fill(data,'Completed','N')
		SimpleTableAdapter.fillemptyfields(self,data)
		

def planninglistitems_generator(conn):
	"""
	Provides a dictionary of possible planning list items
	"""
	cursor=conn.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("""
			SELECT 
			  Left(sigrod.Sigrodid,8) AS StandId, 
			  SUM(sigrod.Hectares) AS TotalHas, 
			  TaskList.TaskId, 
			  sigrod.Cc AS PropId, 
			  Year(Now()) as BudgetYear,
			  TaskList.UnitId 
			FROM TaskList, sigrod
			WHERE (((TaskList.AgeMin)<=(Year(Now())-sigrod.Ano)) 
			  AND ((TaskList.AgeMax)>=(Year(Now())-sigrod.Ano)))
			GROUP BY StandId
			ORDER BY Year(Now())-sigrod.Ano, TaskList.TaskId
			""")
	return cursor.fetchall()


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
		list.add( {'BudgetYear':1978, 'PropId': 1234, 'StandId':2345, 'Quantity':12000, 'UnitId':1, 'TaskId':3456});
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
