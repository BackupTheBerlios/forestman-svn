import MySQLdb
import gettext
gettext.install('ForestMan')

from ForestManPage import ForestManPage

from MiddleLayer.Globals import join
from MiddleLayer.TaskCreator import TaskCreator

from IdLookers import UnitIdLooker, TaskGroupIdLooker
from TableDrawer import TableDrawer

class PlanningPage(ForestManPage, TableDrawer):
	def title(self):
		return _("Planning")
