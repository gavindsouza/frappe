import os
import unittest
import subprocess
import shlex

import io

command_tests = {}


def test_for(command):
	"""
	Decorator for matching a test function to an available command.

	Use as:

		@test_for("new-site")
		def test_new_site_with_app(param1, param2):
			'''Test if specified app is installed when new site is created'''
			# logic
	"""
	def innerfn(fn):
		global command_tests
		try:
			command_tests[command].append(fn)
		except KeyError:
			command_tests[command] = [fn]
		return fn

	return innerfn


@test_for("console")
def test_console(*args, **kwargs):
	import time
	time.sleep(30)
	print("Ill test one feature of console")


@test_for("console")
def test_console_2(*args, **kawrgs):
	print("Ill test another feature of console")


def run(command):
	command = shlex.split(command)
	exec = subprocess.Popen(command)


class BaseCommandTest(unittest.TestCase):
	def setUp(self):
		self.test_execution_environment()

	def test_execution_environment(self):
		"""Check if command executes when executed via a terminal call as well as an API"""
		os.get_terminal_size()

	def tearDown(self):
		pass
		# probably see if its possible to get exit codes, etc? :think:


class CommandTestSuite(unittest.TestSuite):
	pass

class LoggingResult(unittest.TestResult):
	def __init__(self, log):
		self._events = log
		super().__init__()

	def startTest(self, test):
		self._events.append('startTest')
		super().startTest(test)

	def startTestRun(self):
		self._events.append('startTestRun')
		super(LoggingResult, self).startTestRun()

	def stopTest(self, test):
		self._events.append('stopTest')
		super().stopTest(test)

	def stopTestRun(self):
		self._events.append('stopTestRun')
		super(LoggingResult, self).stopTestRun()

	def addFailure(self, *args):
		self._events.append('addFailure')
		super().addFailure(*args)

	def addSuccess(self, *args):
		self._events.append('addSuccess')
		super(LoggingResult, self).addSuccess(*args)

	def addError(self, *args):
		self._events.append('addError')
		super().addError(*args)

	def addSkip(self, *args):
		self._events.append('addSkip')
		super(LoggingResult, self).addSkip(*args)

	def addExpectedFailure(self, *args):
		self._events.append('addExpectedFailure')
		super(LoggingResult, self).addExpectedFailure(*args)

	def addUnexpectedSuccess(self, *args):
		self._events.append('addUnexpectedSuccess')
		super(LoggingResult, self).addUnexpectedSuccess(*args)


class LoggingTextResult(LoggingResult):
	separator2 = ''
	def printErrors(self):
		pass

class LoggingRunner(unittest.TextTestRunner):
	def __init__(self, events):
		super(LoggingRunner, self).__init__(io.StringIO())
		self._events = events

	def _makeResult(self):
		return LoggingTextResult(self._events)


def run_tests(command, config=None):
	events = []
	suite = CommandTestSuite()

	if command == 'all':
		print("{} commands found with tests".format(len(command_tests)))
		for command, tests in command_tests.items():
			for test in tests:
				suite.addTest(test)

	else:
		available_commands = command_tests.get(command, [])
		if not available_commands:
			print("No tests found for {}".format(command))
		for tests in available_commands:
			for test in tests:
				suite.addTest(test)

	runner = LoggingRunner(events)
	runner.run(suite)
