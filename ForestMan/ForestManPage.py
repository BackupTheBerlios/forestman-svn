from WebKit.SidebarPage import SidebarPage
import string, os

import gettext
gettext.install('ForestMan')

class ForestManPage(SidebarPage):

	def __init__(self):
		self.error=None
		SidebarPage.__init__(self)
		
	def cornerTitle(self):
		return _("Forestry Manager v1.0")

	def isDebugging(self):
		return 0


	def writeSidebar(self):
		self.startMenu()
		self.menuItem(_("test"),"http://google.com")
		self.endMenu()


	def title(self):
		return _("Empty ForestMan template")


	def htBodyArgs(self):
		if self.error:
			return SidebarPage.htBodyArgs(self) + """ onload="javascript:alert('""" + self.error.errortext + """')" """
