def createPlanningItems(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS PlanningItems
			(
				PlanningItemId 	INT NOT NULL AUTO_INCREMENT,
				BudgetYear	SMALLINT,
				PropId		TINYINT,
				StandId		CHAR(9),
				Quantity	FLOAT,
				UnitId		SMALLINT,
				TaskId		CHAR(4) NOT NULL,
				YieldFac	FLOAT,
				EstPrice	DECIMAL(14,2),
				PRIMARY KEY (PlanningItemId)
			) ENGINE=InnoDB
			      """)
	return ( 'PlanningItems',
			 ('PlanningItemId','BudgetYear','PropId','StandId','Quantity','UnitId','TaskId','YieldFac','EstPrice'),
			 ('BudgetYear','PropId','StandId','UnitId','TaskId') )

def createPurchaseOrderList(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS PurchaseOrderList
			(
				PurchaseOrder	INT NOT NULL,
				ContractorId	INT,
				StartDate		DATE,
				EndDate			DATE,
				PropId			TINYINT,
				TaskGroupId		TINYINT,
				PRIMARY KEY (PurchaseOrder),
				UNIQUE		(PurchaseOrder)
			)
			""")
	return ( 'PurchaseOrderList',
			 ('PurchaseOrder','ContractorId','StartDate','EndDate','PropId','StandId'),
			 ('PurchaseOrder','ContractorId','StartDate','EndDate','PropId','StandId'))
	
def createContractedItems(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS ContractedItems 
			(
				ContractedItemId 	INT NOT NULL AUTO_INCREMENT,
				PlanningItemId	INT,
				PurchaseOrder	INT,
				ContractedQty	FLOAT,
				ContractedUnitId SMALLINT,
				ContractedUnitPrice 	DECIMAL(14,2),
				Completed		ENUM('N','Y') NOT NULL,
				PRIMARY KEY (ContractedItemId),
				KEY (PurchaseOrder)
			) ENGINE=InnoDB
		       """)

def createContractedTransactions(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS ContractedTransactions
			(
				ContractedTransactionId	INT NOT NULL AUTO_INCREMENT,
				ContractedItemId	INT,
				QtyCompleted		FLOAT,
				CompletionDate		DATE,
				UnitPrice			DECIMAL(14,2),
				PRIMARY KEY (ContractedTransactionId),
				KEY (ContractedItemId)
			) ENGINE=InnoDB
		       """)

def createCertificates(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS Certificates
			(
				CertificateId	INT NOT NULL AUTO_INCREMENT,
				ContractedTransactionId	INT,
				PDF		BLOB,
				PRIMARY KEY (CertificateId),
				KEY (ContractedTransactionId)
			) ENGINE=InnoDB
		       """)

def createInvoices(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS Invoices
			(
				InvoiceId 	INT NOT NULL AUTO_INCREMENT,
				ContractedTransactionId INT,
				InvoiceNo	INT,
				ScaleTicketNo	INT,
				PlateNo		INT,
				Destination	TEXT,
				NoOfLogs	INT,
				LogLength	FLOAT,
				LogDiameterMin	FLOAT,
				LogDiameterMax	FLOAT,
				Checked		ENUM('N','Y') NOT NULL,
				PRIMARY KEY (InvoiceId)
			) ENGINE=InnoDB
		       """)

def createTaskList(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS TaskList
			(
				TaskId		CHAR(4) NOT NULL,
				Description	TINYTEXT,
				UnitId	 	TINYINT,
				AgeMin  	TINYINT,
				AgeMax  	TINYINT,
				TaskGroupId		TINYINT,
				PRIMARY KEY	(TaskId),
				UNIQUE		(TaskId)
			) ENGINE=InnoDB
			       """)

def createTaskGroups(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS TaskGroups
			(
				TaskGroupId	TINYINT NOT NULL AUTO_INCREMENT,
				Name		VARCHAR(32),
				PRIMARY KEY 	(TaskGroupId)
			) ENGINE=InnoDB
			       """)
	return ('TaskGroups',('TaskGroupId','Name'), ('Name',))

def createUnits(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS Units
			(
				UnitId	TINYINT NOT NULL AUTO_INCREMENT,
				Name		VARCHAR(16),
				PRIMARY KEY 	(UnitId)
			) ENGINE=InnoDB
			       """)
	return 'Units',('UnitId','Name'),('Name',)

def createContractors(cursor):
	cursor.execute("""
			CREATE TABLE IF NOT EXISTS Contractors
			(
				ContractorId	INT NOT NULL AUTO_INCREMENT,
				Name 			TINYTEXT,
				Address			TINYTEXT,
				Location		VARCHAR(25),
				CUIT			CHAR(16),
				Phone			VARCHAR(15),
				PRIMARY KEY 	(ContractorId)
			) ENGINE=InnoDB
			       """)
	return 'Contractors',('ContractorId', 'Name', 'Address', 'Location', 'CUIT','Phone'),('Name',)
	

