class IdLookerBase:
	"""
	Helper class for displaying indexed items
	tableinfo class member is a dict with keys
	'TableName' - Name of table with id to displayed text mapping
	'NameField' - Field name of column with the display text
	'IdField' - Field name of column with id's
	"""
	tableinfo = {'TableName':None,'NameField':None,'IdField':None}

	def __init__(self,databaseconnection):
		self.databaseconnection=databaseconnection
		self.cursor=self.databaseconnection.cursor();

	def lookup(self,id):
		t=self.tableinfo
		self.cursor.execute("SELECT "+t['NameField'] +" FROM "+t['TableName']+" WHERE "+t['IdField']+" = %s",id)
		return self.cursor.fetchone()[0]

	def getlist(self):
		t=self.tableinfo
		self.cursor.execute("SELECT "+t['IdField'] +", "+t['NameField']+" FROM "+t['TableName'])
		return self.cursor.fetchall()

class UnitIdLooker(IdLookerBase):
	tableinfo = {'TableName':'Units','NameField':'Name','IdField':'UnitId'}

class TaskGroupIdLooker(IdLookerBase):
	tableinfo = {'TableName':'TaskGroups','NameField':'Name','IdField':'TaskGroupId'}
