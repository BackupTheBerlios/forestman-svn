import sys
import os
import MySQLdb

from TableConstructors import createTaskList, createTaskGroups

try:
	conn = MySQLdb.connect (host = "localhost",
	                       	user = "zope",
				passwd = "zope",
				db = "forestrymanagement")
except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
	sys.exit (1)

try:
	if not os.path.isfile(sys.argv[1]) or os.path.splitext(sys.argv[1])[1] != ".dbf":
		print "need to specify a dbf for the import TaskList as input"
		sys.exit (1)

	cursor=conn.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("DROP TABLE IF EXISTS TaskList"); 
	cursor.execute("DROP TABLE IF EXISTS TaskGroups"); 
	createTaskList(cursor)
	createTaskGroups(cursor)

	if os.system("dbf2mysql -c -d forestrymanagement -t CLS_TAR -U zope -P zope " +sys.argv[1]) != 0:
		print "error executing dbf2mysql"
		sys.exit(1)
	
	cursor.execute( """
				INSERT INTO TaskList (TaskId, Description, Unit,AgeMin,AgeMax)
	 			SELECT	
				  TARID as TaskId, 
				  TARDEN as Description,
				  IF(STRCMP(TARUN,'ha'),
				    IF(STRCMP(TARUN,'ton'),
				      IF(STRCMP(TARUN,'mes'),'','months'),
				    'tonnes'),
				  'hectares') as Unit,
				  TAREDMIN as AgeMin,
				  TAREDMAX as AgeMax
				from CLS_TAR;
				""")

	cursor.execute(""" INSERT INTO TaskGroups (Name)
			   VALUES ('Harvesting'),('Silviculture'),('Others')""")
			  
			   

	cursor.execute( "SELECT * FROM TaskList")
	tl=cursor.fetchall()
	for i in tl:
		group = i['TaskId'][0]
		if group=='p':
			i['GroupId']=1 #yes, i know its an assumption..
		elif group=='v':
			i['GroupId']=3
		elif group=='s':
			i['GroupId']=2
		elif group=='r':
			i['GroupId']=3
		
		cursor.execute("UPDATE TaskList SET GroupId=%(GroupId)s WHERE TaskId=%(TaskId)s",i)

	
		
		


except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
	sys.exit (1)

	conn.close ()
	sys.exit (0)

