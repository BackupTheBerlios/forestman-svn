import string, os
import MySQLdb


import gettext
gettext.install('ForestMan')

class TaskCreator:
	"""
	Middleware object representing the user modifiable list of possible tasks
	"""
	def __init__(self, databaseconnection):
		"""Initialise PlanningList. Takes a DB-API Connection object"""
		self.databaseconnection=databaseconnection
		self.cursor=self.databaseconnection.cursor(MySQLdb.cursors.DictCursor);
		import TableConstructors
		TableConstructors.createTaskList(self.cursor)
		
	def add(self,task):
		"""
		task is a dict which should have keys UnitId, AgeMin, AgeMax, GroupId
		it can optionally have Description
		"""
		assert(task.has_key('TaskId'))
		assert(task.has_key('UnitId'))
		assert(task.has_key('AgeMin'))
		assert(task.has_key('AgeMax'))
		assert(task.has_key('GroupId'))

		def fill(key, val=None):
			if not task.has_key(key):
				task[key]=val
	
		fill('Description',"")

		self.cursor.execute("""	
					INSERT INTO TaskList (
					  TaskId,
					  UnitId,
					  AgeMin,
					  AgeMax,
					  GroupId,
					  Description
					  )
					VALUES (
					  %(TaskId)s,
					  %(UnitId)s,
					  %(AgeMin)s,
					  %(AgeMax)s,
					  %(GroupId)s,
					  %(Description)s
					) """ , task)

	def delete(self,id):
		if type(id)==type(dict()):
			self.cursor.execute("DELETE FROM TaskList "
					    "WHERE TaskId = %(TaskId)s",id);
		elif type(id)==type(int()):
			self.cursor.execute("DELETE FROM TaskList "
					    "WHERE TaskId = %s",id);

	def modify(self, fields ):
		"""
		fields is a dict that may contain any valid key names from this object. 
		Must contain a TaskId
		"""
		assert(fields.has_key('TaskId'))

		s = "UPDATE TaskList SET "
		addcomma=False;
		for name in fields:
			if name != 'TaskId':
				if addcomma:
					s+=", "
				s+=name + " = %("+name+")s "
				addcomma=True
			
		s+="WHERE TaskId = %(TaskId)s"

		self.cursor.execute(s,fields)
	
	def get(self):
		"""
		Returns the TaskList as a dictionary 
		"""
		self.cursor.execute("SELECT * FROM TaskList")
		return self.cursor.fetchall()


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
		list=TaskCreator(conn) 
		list.add( {'TaskId':'vn11','UnitId':1, 'AgeMin':12, 'AgeMax':23, 'GroupId':1});
		print list.get()
		item=list.get()[0];
		item['AgeMax']=24

		list.modify(item);
		print list.get()
		list.delete(item);
		print list.get()
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
