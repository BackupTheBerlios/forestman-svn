import MySQLdb
import sys
from Globals import join


import sys
try:
	conn = MySQLdb.connect	(host = "localhost",
							user = "forestman",
							passwd = "forestman",
							db = "forestman")
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

conn.cursor().execute("DROP TABLE IF EXISTS Units"); 
conn.cursor().execute("DROP TABLE IF EXISTS TaskGroups"); 
conn.cursor().execute("DROP TABLE IF EXISTS TaskList"); 
conn.cursor().execute("DROP TABLE IF EXISTS Contractors"); 
conn.cursor().execute("DROP TABLE IF EXISTS PlanningItems"); 
conn.cursor().execute("DROP TABLE IF EXISTS PurchaseOrderList"); 
conn.cursor().execute("DROP TABLE IF EXISTS ContractedItems"); 
conn.cursor().execute("DROP TABLE IF EXISTS ContractedTransactions"); 
conn.cursor().execute("DROP TABLE IF EXISTS Invoices"); 
conn.cursor().execute("DROP TABLE IF EXISTS Certificates"); 

from UnitList import UnitList
unitlist=UnitList(conn)
hects=unitlist.add({'Name':'Hectares'})
ton=unitlist.add({'Name':'Tonnes'})
mes=unitlist.add({'Name':'Meses'})
seismes=unitlist.add({'Name':'14000 hrs'})

from TaskGroupCreator import TaskGroupCreator
taskgroupcreator=TaskGroupCreator(conn)
prod=taskgroupcreator.add({'Name':'Produccíon'})
silv=taskgroupcreator.add({'Name':'Silviculture'})
other=taskgroupcreator.add({'Name':'Otros'})

from TaskCreator import TaskCreator
taskcreator=TaskCreator(conn)
taskcreator.add(join(hects, prod, {'TaskId':'aa01','AgeMin':12, 'AgeMax':14, 'Description':"do the monkey"}))
taskcreator.add(join(ton, silv, {'TaskId':'bb01','AgeMin':20, 'AgeMax':21, 'Description':"do the monkey1"}))
taskcreator.add(join(hects, prod, {'TaskId':'aa02','AgeMin':12, 'AgeMax':14, 'Description':"do the monkey2"}))
taskcreator.add(join(mes, other, {'TaskId':'aa03','AgeMin':0, 'AgeMax':50, 'Description':"do the monkey3"}))

from PlanningList import PlanningList,planninglistitems_generator
planlist=PlanningList(conn) 
planlist.add(join(planninglistitems_generator(conn)[0],{'Quantity':12, 'EstPrice':100}) );
planlist.add(join(planninglistitems_generator(conn)[1],{'Quantity':12, 'EstPrice':100}) );
planlist.add(join(planninglistitems_generator(conn)[3],{'Quantity':32, 'EstPrice':100}) );
planlist.add(planninglistitems_generator(conn)[3] );


from ContractorCreator import ContractorCreator
cc=ContractorCreator(conn)
con_d=cc.add({'Name':"Dave's Dodgy Dealings"})
con_k=cc.add({'Name':"Kevin's Krazy Kontracting"})
con_s=cc.add({'Name':"Steve's Shifty Silviculture",'CUIT':'0123456789ABCDEF'})

from PurchaseOrderList import PurchaseOrderList
polist=PurchaseOrderList(conn)
if polist.addpurchaseorder({'PurchaseOrder':2342, 'ContractorId':23, 'StartDate':"3/4/89", 'EndDate':"3/4/99",'PropId':07, 'TaskGroupId':1}):
	for i in planlist.get():
		polist.addpurchaseorderitem(join(con_d, {'PlanningItemId':i['PlanningItemId'], 'PurchaseOrder':2342, 'StartDate':"3/4/89", 'EndDate':"3/4/99"}));
else:
	print "add failed for purchase order 2342"
	sys.exit(1)

if polist.addpurchaseorder({'PurchaseOrder':1234, 'ContractorId':23, 'StartDate':"3/4/89", 'EndDate':"3/4/99",'PropId':07, 'TaskGroupId':1}):
	for i in planlist.get():
		polist.addpurchaseorderitem(join(con_d, {'PlanningItemId':i['PlanningItemId'], 'PurchaseOrder':2342, 'StartDate':"3/4/89", 'EndDate':"3/4/99"}));
else:
	print "add failed for purchase order 1234"
	sys.exit(1)
	
from TransactionCreator import TransactionCreator
tc=TransactionCreator(conn, other)
polist.purchaseorder=2342
for i in polist.get()['PurchaseOrderItems']:
	tc.createtransaction({'ContractedItemId':i['ContractedItemId'], 'QtyCompleted':12, 'CompletionDate':30-12-2004})

from HarvesterTransactionCreator import HarvesterTransactionCreator
htc=HarvesterTransactionCreator(conn,silv)
for i in polist.get()['PurchaseOrderItems']:
	trans=htc.createtransaction({'ContractedItemId':i['ContractedItemId'], 'QtyCompleted':12, 'CompletionDate':30-12-2004})
	htc.createinvoice(join(trans,{'InvoiceNo':732645}))

from CertificateCreator import CertificateCreator
certc=CertificateCreator(conn,2342)
posscert= certc.get()
print "Certifiable items for 2342:",posscert
for i in posscert[:3]:
	certc.select(i['ContractedTransactionId'])
print "Certifiable items, some selected, for 2342:",certc.get()

from CertificateCreator import CertificateMaker
certm=CertificateMaker(conn,certc)
print "Certificate preview for selected items",certm.previewcertificate()
certm.generatecertificate()
print "Certifiable items for 2342, after certification:",certc.get()
conn.close ()
sys.exit (0)
