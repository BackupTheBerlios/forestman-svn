import gettext
gettext.install('ForestMan')

from ForestManPage import ForestManPage

class Welcome(ForestManPage):

	def writeContent(self):
		self.writeln(_('<p> Welcome to Forestry Manager !') )
				    
			
