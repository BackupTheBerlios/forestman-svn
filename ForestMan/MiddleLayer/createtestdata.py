import MySQLdb
import sys

from PurchaseOrderList import PurchaseOrderList
from TransactionCreator import TransactionCreator
from PlanningList import PlanningList,planninglistitems_generator

import sys
try:
	conn = MySQLdb.connect	(host = "localhost",
							user = "forestman",
							passwd = "forestman",
							db = "forestman")
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

try:
	
	conn.cursor().execute("DROP TABLE IF EXISTS ContractedItems"); 
	conn.cursor().execute("DROP TABLE IF EXISTS PlanningItems"); 
	conn.cursor().execute("DROP TABLE IF EXISTS ContractedTransactions"); 

	def ap(d,k,v):
		d[k]=v
		return d

	planlist=PlanningList(conn) 
	planlist.add(ap(planninglistitems_generator(conn)[0],'Quantity',12) );
	planlist.add(ap(planninglistitems_generator(conn)[1],'Quantity',12) );
	planlist.add(ap(planninglistitems_generator(conn)[3],'Quantity',32) );
	planlist.add(planninglistitems_generator(conn)[3] );

	polist=PurchaseOrderList(conn) 
	for i in planlist.get():
		polist.add({'PlanningItemId':i['PlanningItemId'], 'PurchaseOrder':2342, 'ContractorId':23, 'StartDate':"3/4/89", 'EndDate':"3/4/99"});
		

	tc=TransactionCreator(conn, "Other")
	for i in polist.get():
		tc.createtransaction({'ContractedItemId':i['ContractedItemId'], 'QtyCompleted':12, 'CompletionDate':30-12-2004})

except MySQLdb.Error, e:
	print "Error %d: %s" % (e.args[0], e.args[1])
	sys.exit (1)

	conn.close ()
	sys.exit (0)

