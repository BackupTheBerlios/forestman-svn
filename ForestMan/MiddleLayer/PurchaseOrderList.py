import sets

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
		TableConstructors.createPurchaseOrderList(self.cursor)
		TableConstructors.createContractedItems(self.cursor)
		TableConstructors.createContractedTransactions(self.cursor)
		TableConstructors.createPlanningItems(self.cursor)
		self.purchaseorder=None		
			
	def addpurchaseorder(self,data):
		"""
		Create a new purchase order with contractor ContractorId, starting at StartDate and ending at EndDate. purchaseorderitem is a dict
		that should contain, at keys 'PurchaseOrder', 'ContractorId', 'StartDate', 'EndDate', 'PropId', 'TaskGroupId'
		returns True if succeded and sets current purchaseorder to this new purchaseorder
		"""
		try:
			self.cursor.execute("""	
					INSERT INTO PurchaseOrderList (PurchaseOrder, ContractorId, StartDate, EndDate, PropId, TaskGroupId)
					VALUES (%(PurchaseOrder)s,%(ContractorId)s,%(StartDate)s,%(EndDate)s,%(PropId)s,%(TaskGroupId)s)	
					""",data)
		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			return False
		
		self.purchaseorder=data['PurchaseOrder']
		return True
	
	def addpurchaseorderitem(self,purchaseorderitem):
		"""
		Add new item from a purchase order to the current, which is a fulfilment of planned item planninglistid, 
		with contractor contractorid, starting at start and ending at end. purchaseorderitem is a dict
		that should contain at least the key 'PlanningItemId' for the planning item this is fulfilling 
		and optionally 'ContractorQty', 'ContractedUnit', 'ContractedUnitPrice'. These will be filled in automatically
		from the PlanningItem if not given
		returns a dict with the ContractedItemId of the new entry
		"""

		assert(self.purchaseorder != None)
		assert(purchaseorderitem.has_key('PlanningItemId'))
	
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
		purchaseorderitem['PurchaseOrder']=self.purchaseorder

		self.cursor.execute("""	
					INSERT INTO ContractedItems (PlanningItemId,PurchaseOrder,ContractedQty,ContractedUnitId,ContractedUnitPrice)
					VALUES (%(PlanningItemId)s,%(PurchaseOrder)s,%(ContractedQty)s,%(ContractedUnitId)s,%(ContractedUnitPrice)s)	
					""",purchaseorderitem)

		self.cursor.execute("SELECT LAST_INSERT_ID()")
		last_insert_id=self.cursor.fetchone()['LAST_INSERT_ID()']
		return {'ContractedItemId':last_insert_id}


	def deletePO(self, *args):
		"""deletes the given purchaseorder. default is to delete the current purchase order"""
		if args:
			purchaseorder=args[0]
		else:
			purchaseorder=self.purchaseorder
			self.purchaseorder = None
		self.cursor.execute("DELETE FROM ContractedItems WHERE PurchaseOrder= %s", purchaseorder);
		self.cursor.execute("DELETE FROM PurchaseOrderList WHERE PurchaseOrder= %s", purchaseorder);
		
	def deletepurchaseorderitem(self,id):
		if type(id)==type(dict()):
			self.cursor.execute("DELETE FROM ContractedItems "
					    "WHERE ContractedItemId = %(ContractedItemId)s",id);
		elif type(id)==type(int()):
			self.cursor.execute("DELETE FROM ContractedItems "
					    "WHERE ContractedItemId = %s",id);

	def modify(self,fields):
		"""
		fields is a dict that may contain any valid key names from this object. 
		if it contains a ContractedItemId, it is taken as a modifeir for a purchase orser item, and in this case
		- if transactions have started on the contracted item, only 'Notes' and 'Completed' are modifiable.
		- if modifications of other datas are requested after this point, they will be ignored
		if it contains any on the base keys returned by 'get', these are modifed  
		"""
		if fields.has_key('ContractedItemId'):

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
			self.cursor.execute(s,fields)
		else:
			inset=sets.Set(fields.keys())
			outset=sets.Set(['ContractorId', 'StartDate', 'EndDate', 'PropId', 'TaskGroupId'])
			inters = outset & inset
			if inters:
				s = "UPDATE PurchaseOrderList SET "
				addcomma=False;
				for name in inters:
					if addcomma:
						s+=", "
					s+=name + " = %("+name+")s "
					addcomma=True
				if not fields['PurchaseOrder']:
					fields['PurchaseOrder']=self.purchaseorder
				s+="WHERE PurchaseOrder = %(PurchaseOrder)s"
				self.cursor.execute(s,fields)
					
				
	
	def get(self):
		"""
		Returns the curret PurchaseOrder as a dictionary containing keys
		'PurchaseOrder', 'ContractorId', 'StartDate', 'EndDate', 'PropId', 'TaskGroupId'
		and 'PurchaseOrderItems'
		'PurchaseOrderItems' is a table of ContractedItems plus RunningTotal and RemainingQty
		"""
		assert(self.purchaseorder != None)

		self.cursor.execute("SELECT * from PurchaseOrderList WHERE PurchaseOrder=%s",self.purchaseorder)
		ret=self.cursor.fetchone()

		if ret == None:
			return None
				
		self.cursor.execute("SELECT * FROM ContractedItems WHERE PurchaseOrder = %s",self.purchaseorder)
		purchaseorderitems= self.cursor.fetchall()
		for i in purchaseorderitems:
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
		
		ret['PurchaseOrderItems']=purchaseorderitems

		return ret		


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
		conn.cursor().execute("DROP TABLE IF EXISTS ContractedItems"); 
		conn.cursor().execute("DROP TABLE IF EXISTS PurchaseOrderList"); 
		list=PurchaseOrderList(conn) 
		if list.addpurchaseorder({'PurchaseOrder':2342, 'ContractorId':23, 'StartDate':"3/4/89", 'EndDate':"3/4/99",'PropId':07, 'TaskGroupId':1}):
			list.addpurchaseorderitem({'PlanningItemId':1});
			list.addpurchaseorderitem({'PlanningItemId':2});
			list.addpurchaseorderitem({'PlanningItemId':3});
			list.addpurchaseorderitem({'PlanningItemId':4});
		else:
			print "add failed for purchase order 2342"
		if list.addpurchaseorder({'PurchaseOrder':1234, 'ContractorId':23, 'StartDate':"3/4/89", 'EndDate':"3/4/99",'PropId':07, 'TaskGroupId':1}):
			list.addpurchaseorderitem({'PlanningItemId':5});
			list.addpurchaseorderitem({'PlanningItemId':6});
			list.addpurchaseorderitem({'PlanningItemId':7});
			list.addpurchaseorderitem({'PlanningItemId':8});
			print list.get()
			item=list.get()['PurchaseOrderItems'][0]
			item.update({'ContractedQty':3400, 'ContractedUnitId':1, 'ContractedUnitPrice':23.54})
			list.modify(item)
			print list.get()
			list.deletepurchaseorderitem(item)
			print list.get()
		else:
			print "add failed for purchase order 1234"
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

	conn.close ()
	sys.exit (0)
