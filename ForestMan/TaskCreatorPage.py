import MySQLdb
import gettext
gettext.install('ForestMan')

from ForestManPage import ForestManPage

from MiddleLayer.Globals import join
from MiddleLayer.TaskCreator import TaskCreator

from IdLookers import UnitIdLooker, TaskGroupIdLooker
from TableDrawer import TableDrawer

class TaskCreatorPage(ForestManPage, TableDrawer):
	def title(self):
		return _("Task Creator Page")

	def __init__(self):
		conn = MySQLdb.connect	(host = "localhost",
								user = "forestman",
								passwd = "forestman",
								db = "forestman")
		ForestManPage.__init__(self)
		TableDrawer.__init__(self,conn)
		unitidlooker = UnitIdLooker(conn)
		taskgroupidlooker = TaskGroupIdLooker(conn)
		self.taskcreator=TaskCreator(conn)
		self.fields = [[_("Task Id"),"TaskId"],
				  [_("Description"),"Description"],
				  [_("Task Group"),"TaskGroup",taskgroupidlooker],
				  [_("Unit"),"Unit",unitidlooker],
				  [_("Min Age"),"AgeMin"],
				  [_("Max Age"),"AgeMax"]]
		self.idfield="TaskId"

	def add(self,f):
		self.taskcreator.add(f)
			
	def modify(self,f):
		self.taskcreator.modify(f)
		
	def writeContent(self):
		self.writeTable()			

	def actions(self):
		return ForestManPage.actions(self) + TableDrawer.actions(self)