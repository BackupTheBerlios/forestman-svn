import string, os
import MySQLdb


import gettext
gettext.install('ForestMan')

class SimpleTableAdapter:
	"""
	Makes a middleware object from a simple table
	"""
	def __init__(self, databaseconnection,tableconstructor):
		"""Initialise table adaptor. Takes a DB-API Connection object"""
		self.databaseconnection=databaseconnection
		self.cursor=self.databaseconnection.cursor(MySQLdb.cursors.DictCursor);
		import TableConstructors
		#check the table exists and get the name and fields. we assume the 1st field is the primary index
		self.name, self.fields,self.necessaryfields =tableconstructor(self.cursor)
		
	def add(self,data):
		"""
		data is a dict of the row to add
		"""
		for i in self.necessaryfields:
			assert (data.has_key(i))

		self.fillemptyfields(data)
		
		query_top = "INSERT INTO "+self.name+ " ("
		query_bottom = ") VALUES ("

		addcomma=False;
		for i in self.fields[1:]:
			if addcomma:
				query_top+=", "
				query_bottom+=", "
			query_top+=i
			query_bottom += "%("+i+")s"
			addcomma=True

		query=query_top+query_bottom+")"
		self.cursor.execute(query , data)

	def delete(self,id):
		if type(id)==type(dict()):
			self.cursor.execute("DELETE FROM " + self.name +
					    " WHERE "+self.fields[0] +" = %("+ self.fields[0]+")s",id);
		elif type(id)==type(int()):
			self.cursor.execute("DELETE FROM " + self.name +
					    " WHERE "+self.fields[0] +" = %s",id);

	def modify(self, data ):
		"""
		fields is a dict that may contain any valid key names from this object. 
		Must contain an index
		"""
		assert(data.has_key(self.fields[0]))

		s = "UPDATE "+self.name+" SET "
		addcomma=False;
		for name in data:
			if name != self.fields[0]:
				if addcomma:
					s+=", "
				s+=name + " = %("+name+")s "
				addcomma=True
			
		s+="WHERE "+self.fields[0]+" = %(" + self.fields[0] +")s"

		self.cursor.execute(s,data)
	
	def get(self):
		"""
		Returns the table as a dictionary 
		"""
		self.cursor.execute("SELECT * FROM " +self.name)
		return self.cursor.fetchall()

	def fillemptyfields(self,data):
		"""
		this function should be overloaded to fill in non-necessary fields that
		the user failed to pass into an add. Default action is raise an error if there
		are empty fields
		"""
		for i in self.fields[1:]:
			assert(data.has_key(i))

	def fill(self,data, key, val=None):
		"Helper funtion for basic fillemptyfields implementations"
		if not data.has_key(key):
			data[key]=val			