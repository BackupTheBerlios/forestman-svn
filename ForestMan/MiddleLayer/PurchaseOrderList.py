import string, os
import MySQLdb

import gettext
gettext.install('ForestMan')

class PurchaseOrderList:
	"""
  	Middleware object representing the user input list of purchase orders 
	"""
	def __init__(self, databaseconnection):
		"""Initialise PurchaseOrderList. Takes a DB-API Connection object"""
		self.databaseconnection=databaseconnection
		self.cursor=self.databaseconnection.cursor(MySQLdb.cursors.DictCursor);
		import TableConstructors
		TableConstructors.createContractedItems(self.cursor)
		TableConstructors.createContractedTransactions(self.cursor)
		TableConstructors.createPlanningItems(self.cursor)
		
		
	
	def add(self,purchaseorderitem):
		"""
		Add new purchase order to the list, which is a fulfilment of planned item planninglistid, 
		with contractor contractorid, starting at start and ending at end. purchaseorderitem is a dict
		that should contain, at least, keys 'PlanningItemId', 'PurchaseOrder', 'ContractorId', 'StartDate', 'EndDate', 
		and optionally 'ContractorQty', 'ContractedUnit', 'ContractedUnitPrice'
		"""

		assert(purchaseorderitem.has_key('PlanningItemId'))
		assert(purchaseorderitem.has_key('PurchaseOrder'))
		assert(purchaseorderitem.has_key('ContractorId'))
		assert(purchaseorderitem.has_key('StartDate'))
		assert(purchaseorderitem.has_key('EndDate'))

		def fillkey(keyname, columnname):
			if not purchaseorderitem.has_key(keyname):
				self.cursor.execute("SELECT "+columnname+" FROM PlanningItems WHERE "
						    "PlanningItemId = %(PlanningItemId)s", purchaseorderitem)
				if self.cursor.rowcount > 0:
					purchaseorderitem[keyname]=self.cursor.fetchall()[0][columnname]
				else:
					purchaseorderitem[keyname]=None	

		fillkey('ContractedQty', "Quantity")
		fillkey('ContractedUnitId', "UnitId")
		fillkey('ContractedUnitPrice', "EstPrice")

		self.cursor.execute("""	
					INSERT INTO ContractedItems (PlanningItemId,PurchaseOrder,ContractorId,ContractedQty,ContractedUnit,ContractedUnitPrice,StartDate,EndDate)
					VALUES (%(PlanningItemId)s,%(PurchaseOrder)s,%(ContractorId)s,%(ContractedQty)s,%(ContractedUnit)s,%(ContractedUnitPrice)s,%(StartDate)s,%(EndDate)s)	
				    """,purchaseorderitem)

	def deleteByPO(self,purchaseorder):
		self.cursor.execute("DELETE FROM ContractedItemList WHERE PurchaseOrder= %s", purchaseorder);

	def delete(self,id):
		if type(id)==type(dict()):
			self.cursor.execute("DELETE FROM ContractedItems "
					    "WHERE ContractedItemId = %(ContractedItemId)s",id);
		elif type(id)==type(int()):
			self.cursor.execute("DELETE FROM ContractedItems "
					    "WHERE ContractedItemId = %s",id);

	def modify(self,fields):
		"""
		fields is a dict that may contain any valid key names from this object. 
		Must contain a ContractedItemId
		If transactions have started on the contracted item, only 'Notes' and 'Completed' are modifiable.
		if modifications of other datas are requested after this point, they will be ignored
		"""
		assert(fields.has_key('ContractedItemId'))

		#find out if transactions have started
		self.cursor.execute("SELECT * FROM ContractedTransactions "
						   "WHERE ContractedItemId = %(ContractedItemId)s",
						  fields)
		if self.cursor.rowcount >0:
			fields={'Notes':fields['Notes'],'Completed':fields['Completed'], 'ContractedItemId':fields['ContractedItemId']}


		s = "UPDATE ContractedItems SET "
		addcomma=False;
		for name in fields:
			if (name != 'ContractedItemId') and (name != 'RemainingQty') and (name != 'RunningTotal'):
				if addcomma:
					s+=", "
				s+=name + " = %("+name+")s "
				addcomma=True
			
		s+="WHERE ContractedItemId = %(ContractedItemId)s"
		print s
		self.cursor.execute(s,fields)
	
	def get(self):
		"""
		Returns the PurchaseOrderList as a dictionary 
		"""
		self.cursor.execute("SELECT * FROM ContractedItems")
		retval= self.cursor.fetchall()
		for i in retval:
			self.cursor.execute("SELECT SUM(QtyCompleted) AS RunningTotal FROM ContractedTransactions "
						   "WHERE ContractedItemId = %(ContractedItemId)s",
						   i)
			assert(self.cursor.rowcount >0)
			total=self.cursor.fetchall()[0]['RunningTotal']
			if total==None:
				total=0
				
			i['RunningTotal']=total
			if  i['ContractedQty']!= None:
				i['RemainingQty']=i['ContractedQty']-total
			else:
				i['RemainingQty']=None

		return retval

if __name__ == "__main__":
	import sys
	try:
		conn = MySQLdb.connect (host = "localhost",
	       	                 	user = "test",
								passwd="test",
					db = "test")
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	try:
		conn.cursor().execute("DROP TABLE IF EXISTS ContractedItems"); 
		list=PurchaseOrderList(conn) 
		list.add({'PlanningItemId':1, 'PurchaseOrder':2342, 'ContractorId':23, 'StartDate':"3/4/89", 'EndDate':"3/4/99"});
		print list.get()
		item=list.get()[0]
		item.update({'ContractedQty':3400, 'ContractedUnit':'hectares', 'ContractedUnitPrice':23.54})
		list.modify(item)
		print list.get()
		list.delete(item)
		print list.get()
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
