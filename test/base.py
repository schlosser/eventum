import unittest
import os
import mongoengine
from coverage import coverage
from sys import path
path.append('../')
from app import register_blueprints
from app import create_app as create_app_base
from app.mod_auth.models import User
from config import basedir

GPLUS_IDS = {
	'user': 'user123',
	'editor': 'editor123',
	'publisher': 'publisher123',
	'admin': 'admin123'
}
USERS = {
	'user': User(name='Test User',
				  email='user@te.st',
				  gplus_id=GPLUS_IDS['user']),
	'editor': User(name='Test Editor',
				   email='editor@te.st',
				   privelages='editor',
				   gplus_id=GPLUS_IDS['editor']),
	'publisher': User(name='Test Publisher',
					  email='publisher@te.st',
					  privelages='publisher',
					  gplus_id=GPLUS_IDS['publisher']),
	'admin': User(name='Test Admin',
				  email='admin@te.st',
				  privelages='admin',
				  gplus_id=GPLUS_IDS['admin'])
}

def create_test_app():
	"""Creates the app using testing configs"""
	return create_app_base(
		MONGODB_SETTINGS={'DB': 'testing'},
		TESTING=True,
		CSRF_ENABLED=False,
	)



class TestingTemplate(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		""" Sets up a test database before each set of tests """
		create_test_app()
		register_blueprints()
		from app import app
		self.app = app

	@classmethod
	def tearDownClass(self):
		""" Drops the test database after the classes' tests are finished"""

	def request_with_role(self, path, method='GET', role='admin',
						  *args, **kwargs):
		""" Make an http request with the given role's gplus_id
		in the session
		"""
		with self.app.test_client() as c:
			with c.session_transaction() as sess:
				User.drop_collection()

				self.assertEqual(User.objects().count(), 0)

				if role in USERS:
					# if it isn't, the request is without a role
					USERS[role].save()
					sess['gplus_id'] = GPLUS_IDS[role]
				kwargs['method'] = method
				kwargs['path'] = path
			return c.open(*args, **kwargs)

	def test_create_test_app(self):
		create_test_app()
		from app import app
		assert app.config['TESTING']
		assert mongoengine.connection.get_db().name == 'testing'


	@classmethod
	def main(self):
		cov = coverage(branch=True, omit=['../test.py', '../test/*', '../lib/*',
										  '../include/*', '../bin/*'])
		cov.start()
		try:
			unittest.main()
		except:
			pass
		cov.stop()
		cov.save()
		print "\n\nCoverage Report:\n"
		cov.report()
		print "HTML version: " + \
			os.path.join(basedir, "tmp/coverage/index.html")
		cov.html_report(directory='tmp/coverage')
		cov.erase()


if __name__ == '__main__':
	TestingTemplate.main()
