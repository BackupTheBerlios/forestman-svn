from WebKit.SidebarPage import SidebarPage
import string, os

import gettext
gettext.install('ForestMan')

class ForestManPage(SidebarPage):

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

	def writeErrorBody(self,error):
		self.writeln('<h1>')
		self.writeln(_("An error occurred"))
		self.writeln('</h1>')
		self.writeln(error.errortext)
