#!C:\Python23\python.exe

import os, sys

webwarePath = 'C:/forestal/Webware-0.8.1'
appWorkPath = 'c:/forestal/ForestManApp'
sys.path.append('c:/forestal/ForestManApp\\lib')


def main(args):
	global webwarePath, appWorkPath
	newArgs = []
	for arg in args:
		if arg.startswith('--webware-path='):
			webwarePath = arg[15:]
		elif arg.startswith('--working-path='):
			appWorkPath = arg[15:]
		else:
			newArgs.append(arg)
	args = newArgs
	# ensure Webware is on sys.path
	sys.path.insert(0, webwarePath)

	# import the master launcher
	import WebKit.Launch

	if len(args) < 2:
		WebKit.Launch.usage()

	# Go!
	WebKit.Launch.launchWebKit(args[1], appWorkPath, args[2:])


if __name__=='__main__':
	main(sys.argv)
