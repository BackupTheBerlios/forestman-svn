import gettext
gettext.install('ForestMan')

from MiddleLayer.Globals import MiddleLayerError

class TableDrawer:
	"""
	Derived classes should provide a object member called fields that is a list of column definitions.
	Each column definition consists of a list of the displayed name, a number signifying: read/write(0),
	read only(1), read-only but allow a value on creation(2); the data name, and optionally a idlooker
	For stright columns the data name should be the name of the column in the database
	for idloopkup columns it should be a different name that doesnt clash with anything else in the table
	(the actual data name will be derived from the idlooker).
	Derived classes should also provide an class member 'idfield' and member funtions 'add' and 'modify'
	which should take a dict of fields to add or modify for this table.
	This is meant as a mixin class, and derivitives should also derive from Page, it should also
	provide an actions method that indirects down to the actions for this class
	"""
	def __init__(self,conn):
		self.conn=conn
		self.edit=False

	def writeTable(self):
		wr = self.writeln
		wr('<table border=1 cellpadding=0 cellspacing=0 width=100%>')
		wr('<thead><tr>')
		for i in self.fields:
			wr('<th align=center >%s</td>' % i[0])
		wr('</tr></thead>')

		req = self.request()
		print "fields=", req.fields()

		def dolist(looker,fields):
			wr("<td><select size=1 name=%s>"%looker.tableinfo['IdField'])
			for i in looker.getlist():
				if (i[0]==fields[looker.tableinfo['IdField']]):
					wr("<option VALUE=%s SELECTED>%s</option>" % i)
				else:
					wr("<option VALUE=%s>%s</option>" % i)

		def addlookup(looker,fields,name):
			fields.update({name:looker.lookup(fields[looker.tableinfo['IdField']])})

		wr('<tbody>')		
		for i in self.taskcreator.get():
			if self.edit and i[self.idfield]==req.field('id'):
				wr("<tr><form method=post>")
				for j in self.fields:
					if j[1]==0:
						if len(j)>=4:
							dolist(j[3],i)
						else:
							wr("<td><input type=text name=%s value='%s'></td>"%(j[2],i[j[2]]))
					else:
						if len(j)>=4:
							addlookup(j[3],i,j[2])
						
						wr("<td><input type=hidden name=%s value='%s'>%s</td>" %(j[2],i[j[2]],i[j[2]]))
				wr("<td><input type=submit name=_action_changerow value='%s'></td>" % _("Change"))
				wr("</form></tr>")
				wr('<tr>')
			else:
				wr('<tr>')
				wr('<form method=post>')
				wr("<input type=hidden name=id value='%s'>" % i[self.idfield])

				for j in self.fields:
					if len(j)>=4:
						addlookup(j[3],i,j[2])
					
					wr("<td>%s</td>" %i[j[2]])
	
				wr("<td><input type=submit name=_action_editrow value='%s'></td>" % _("Edit") )
				wr("</form>")
				wr('</tr>')

		if not self.edit:
			wr("<tr><form method=post>")
			for j in self.fields:
				if j[1]==0 or j[1]==2:
					if len(j)>=4:
						wr("<td><select size=1 name=%s>" % j[3].tableinfo['IdField'])
						for i in j[3].getlist():
							wr("<option VALUE=%s>%s</option>" % i)
						wr("</td>")
					else:
						wr("<td><input type=text name=%s></td>"%j[2])
				else:
					wr("<td></td>")

			wr("<td><input type=submit name=_action_addrow value='%s'></td>" % _("Add"))
			wr("</form></tr>")

		wr('</tbody>')		


	def addrow(self):
		f = self.request().fields()
		try:
			self.add(f)
		except MiddleLayerError,e:
			self.error = e
		self.writeBody()
		self.error=None

	def changerow(self):
		f = self.request().fields()
		try:
			self.modify(f)
		except MiddleLayerError,e:
			self.error=e
		self.edit=False
		self.writeBody()
		self.error=None

	def editrow(self):
		self.edit=True
		self.writeBody()
		
	def actions(self):
		return  ['addrow','changerow','editrow']
		