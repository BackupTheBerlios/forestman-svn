import os, re, sys, win32serviceutil

# settings
appWorkPath = os.environ['FORESTMANPATH']
webwarePath = os.environ['WEBWAREPATH']
serviceName = 'ForestMan'
serviceDisplayName = 'ForestMan App Server'

# ensure Webware is on sys.path
sys.path.insert(0, webwarePath)

# Construct customized version of ThreadedAppServerService that uses our
# specified service name, service display name, and working dir
from WebKit.ThreadedAppServerService import ThreadedAppServerService
class NTService(ThreadedAppServerService):
	_svc_name_ = serviceName
	_svc_display_name_ = serviceDisplayName
	def workDir(self):
		return appWorkPath

# Handle the command-line args
if __name__=='__main__':
	win32serviceutil.HandleCommandLine(NTService)
