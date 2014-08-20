import os
import os.path
import tempfile
import shutil
from nose.tools import eq_
from nose.tools import with_setup
from build_pack_utils import utils
from compile_helpers import setup_webdir_if_it_doesnt_exist
from compile_helpers import convert_php_extensions
from compile_helpers import build_php_environment
from compile_helpers import is_web_app
from compile_helpers import find_stand_alone_app_to_run
from compile_helpers import load_binary_index
from compile_helpers import find_all_php_versions
from compile_helpers import find_all_php_extensions
from compile_helpers import validate_php_version
from compile_helpers import validate_php_extensions


class TestCompileHelpers(object):
    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='build-')
        self.cache_dir = tempfile.mkdtemp(prefix='cache-')
        os.rmdir(self.build_dir)  # delete otherwise copytree complains
        os.rmdir(self.cache_dir)  # cache dir does not exist normally

    def tearDown(self):
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
        for name in os.listdir(os.environ['TMPDIR']):
            if name.startswith('httpd-') and name.endswith('.gz'):
                os.remove(os.path.join(os.environ['TMPDIR'], name))
            if name.startswith('php-') and name.endswith('.gz'):
                os.remove(os.path.join(os.environ['TMPDIR'], name))

    def assert_exists(self, *args):
        eq_(True, os.path.exists(os.path.join(*args)),
            "Does not exists: %s" % os.path.join(*args))

    @with_setup(setup=setUp, teardown=tearDown)
    def test_setup_if_webdir_exists(self):
        shutil.copytree('tests/data/app-1', self.build_dir)
        setup_webdir_if_it_doesnt_exist(utils.FormattedDict({
            'BUILD_DIR': self.build_dir,
            'WEBDIR': 'htdocs',
            'LIBDIR': 'lib'
        }))
        self.assert_exists(self.build_dir, 'htdocs')
        self.assert_exists(self.build_dir, 'htdocs', 'index.php')
        self.assert_exists(self.build_dir, 'htdocs', 'info.php')
        self.assert_exists(self.build_dir, 'htdocs',
                           'technical-difficulties1.jpg')
        self.assert_exists(self.build_dir, '.bp-config')
        self.assert_exists(self.build_dir, '.bp-config', 'options.json')
        self.assert_exists(self.build_dir, '.bp-config', 'httpd', 'extra',
                           'httpd-remoteip.conf')
        eq_(2, len(os.listdir(self.build_dir)))
        eq_(3, len(os.listdir(os.path.join(self.build_dir, 'htdocs'))))

    @with_setup(setup=setUp, teardown=tearDown)
    def test_setup_if_custom_webdir_exists(self):
        shutil.copytree('tests/data/app-6', self.build_dir)
        setup_webdir_if_it_doesnt_exist(utils.FormattedDict({
            'BUILD_DIR': self.build_dir,
            'WEBDIR': 'public',
            'LIBDIR': 'lib'
        }))
        self.assert_exists(self.build_dir, 'public')
        self.assert_exists(self.build_dir, 'public', 'index.php')
        self.assert_exists(self.build_dir, 'public', 'info.php')
        self.assert_exists(self.build_dir, 'public',
                           'technical-difficulties1.jpg')
        self.assert_exists(self.build_dir, '.bp-config')
        self.assert_exists(self.build_dir, '.bp-config', 'options.json')
        self.assert_exists(self.build_dir, '.bp-config', 'httpd', 'extra',
                           'httpd-remoteip.conf')
        eq_(3, len(os.listdir(self.build_dir)))
        eq_(3, len(os.listdir(os.path.join(self.build_dir, 'public'))))

    @with_setup(setup=setUp, teardown=tearDown)
    def test_setup_if_htdocs_does_not_exist(self):
        shutil.copytree('tests/data/app-2', self.build_dir)
        setup_webdir_if_it_doesnt_exist(utils.FormattedDict({
            'BUILD_DIR': self.build_dir,
            'WEBDIR': 'htdocs',
            'LIBDIR': 'lib'
        }))
        self.assert_exists(self.build_dir, 'htdocs')
        self.assert_exists(self.build_dir, 'htdocs', 'index.php')
        self.assert_exists(self.build_dir, 'htdocs', 'info.php')
        self.assert_exists(self.build_dir, 'htdocs',
                           'technical-difficulties1.jpg')
        self.assert_exists(self.build_dir, '.bp-config')
        self.assert_exists(self.build_dir, '.bp-config', 'options.json')
        self.assert_exists(self.build_dir, '.bp-config', 'httpd', 'extra',
                           'httpd-remoteip.conf')
        eq_(2, len(os.listdir(self.build_dir)))
        eq_(3, len(os.listdir(os.path.join(self.build_dir, 'htdocs'))))

    @with_setup(setup=setUp, teardown=tearDown)
    def test_setup_if_custom_webdir_does_not_exist(self):
        shutil.copytree('tests/data/app-2', self.build_dir)
        setup_webdir_if_it_doesnt_exist(utils.FormattedDict({
            'BUILD_DIR': self.build_dir,
            'WEBDIR': 'public',
            'LIBDIR': 'lib'
        }))
        self.assert_exists(self.build_dir, 'public')
        self.assert_exists(self.build_dir, 'public', 'index.php')
        self.assert_exists(self.build_dir, 'public', 'info.php')
        self.assert_exists(self.build_dir, 'public',
                           'technical-difficulties1.jpg')
        self.assert_exists(self.build_dir, '.bp-config')
        self.assert_exists(self.build_dir, '.bp-config', 'options.json')
        self.assert_exists(self.build_dir, '.bp-config', 'httpd', 'extra',
                           'httpd-remoteip.conf')
        eq_(2, len(os.listdir(self.build_dir)))
        eq_(3, len(os.listdir(os.path.join(self.build_dir, 'public'))))

    @with_setup(setup=setUp, teardown=tearDown)
    def test_setup_if_htdocs_does_not_exist_with_extensions(self):
        shutil.copytree('tests/data/app-4', self.build_dir)
        setup_webdir_if_it_doesnt_exist(utils.FormattedDict({
            'BUILD_DIR': self.build_dir,
            'WEBDIR': 'htdocs',
            'LIBDIR': 'lib'
        }))
        self.assert_exists(self.build_dir, 'htdocs')
        self.assert_exists(self.build_dir, 'htdocs', 'index.php')
        self.assert_exists(self.build_dir, 'htdocs', 'info.php')
        self.assert_exists(self.build_dir, 'htdocs',
                           'technical-difficulties1.jpg')
        self.assert_exists(self.build_dir, '.bp-config')
        self.assert_exists(self.build_dir, '.bp-config', 'options.json')
        self.assert_exists(self.build_dir, '.bp-config', 'httpd', 'extra',
                           'httpd-remoteip.conf')
        self.assert_exists(self.build_dir, '.bp')
        self.assert_exists(self.build_dir, '.bp', 'logs')
        self.assert_exists(self.build_dir, '.bp', 'logs', 'some.log')
        self.assert_exists(self.build_dir, '.extensions')
        self.assert_exists(self.build_dir, '.extensions', 'some-ext')
        self.assert_exists(self.build_dir, '.extensions', 'some-ext',
                           'extension.py')
        eq_(4, len(os.listdir(self.build_dir)))
        eq_(3, len(os.listdir(os.path.join(self.build_dir, 'htdocs'))))

    @with_setup(setup=setUp, teardown=tearDown)
    def test_setup_if_custom_webdir_does_not_exist_with_extensions(self):
        shutil.copytree('tests/data/app-4', self.build_dir)
        setup_webdir_if_it_doesnt_exist(utils.FormattedDict({
            'BUILD_DIR': self.build_dir,
            'WEBDIR': 'public',
            'LIBDIR': 'lib'
        }))
        self.assert_exists(self.build_dir, 'public')
        self.assert_exists(self.build_dir, 'public', 'index.php')
        self.assert_exists(self.build_dir, 'public', 'info.php')
        self.assert_exists(self.build_dir, 'public',
                           'technical-difficulties1.jpg')
        self.assert_exists(self.build_dir, '.bp-config')
        self.assert_exists(self.build_dir, '.bp-config', 'options.json')
        self.assert_exists(self.build_dir, '.bp-config', 'httpd', 'extra',
                           'httpd-remoteip.conf')
        self.assert_exists(self.build_dir, '.bp')
        self.assert_exists(self.build_dir, '.bp', 'logs')
        self.assert_exists(self.build_dir, '.bp', 'logs', 'some.log')
        self.assert_exists(self.build_dir, '.extensions')
        self.assert_exists(self.build_dir, '.extensions', 'some-ext')
        self.assert_exists(self.build_dir, '.extensions', 'some-ext',
                           'extension.py')
        eq_(4, len(os.listdir(self.build_dir)))
        eq_(3, len(os.listdir(os.path.join(self.build_dir, 'public'))))

    def test_setup_if_htdocs_with_stand_alone_app(self):
        shutil.copytree('tests/data/app-5', self.build_dir)
        setup_webdir_if_it_doesnt_exist(utils.FormattedDict({
            'BUILD_DIR': self.build_dir,
            'WEB_SERVER': 'none'
        }))
        self.assert_exists(self.build_dir, 'app.php')
        eq_(1, len(os.listdir(self.build_dir)))

    def test_convert_php_extensions_54(self):
        ctx = {
            'PHP_VERSION': '5.4.x',
            'PHP_EXTENSIONS': ['mod1', 'mod2', 'mod3'],
            'ZEND_EXTENSIONS': ['zmod1', 'zmod2']
        }
        convert_php_extensions(ctx)
        eq_('extension=mod1.so\nextension=mod2.so\nextension=mod3.so',
            ctx['PHP_EXTENSIONS'])
        eq_('zend_extension="@HOME/php/lib/php/extensions/'
            'no-debug-non-zts-20100525/zmod1.so"\n'
            'zend_extension="@HOME/php/lib/php/extensions/'
            'no-debug-non-zts-20100525/zmod2.so"',
            ctx['ZEND_EXTENSIONS'])

    def test_convert_php_extensions_55(self):
        ctx = {
            'PHP_VERSION': '5.5.x',
            'PHP_EXTENSIONS': ['mod1', 'mod2', 'mod3'],
            'ZEND_EXTENSIONS': ['zmod1', 'zmod2']
        }
        convert_php_extensions(ctx)
        eq_('extension=mod1.so\nextension=mod2.so\nextension=mod3.so',
            ctx['PHP_EXTENSIONS'])
        eq_('zend_extension="zmod1.so"\nzend_extension="zmod2.so"',
            ctx['ZEND_EXTENSIONS'])

    def test_convert_php_extensions_54_none(self):
        ctx = {
            'PHP_VERSION': '5.4.x',
            'PHP_EXTENSIONS': [],
            'ZEND_EXTENSIONS': []
        }
        convert_php_extensions(ctx)
        eq_('', ctx['PHP_EXTENSIONS'])
        eq_('', ctx['ZEND_EXTENSIONS'])

    def test_convert_php_extensions_55_none(self):
        ctx = {
            'PHP_VERSION': '5.5.x',
            'PHP_EXTENSIONS': [],
            'ZEND_EXTENSIONS': []
        }
        convert_php_extensions(ctx)
        eq_('', ctx['PHP_EXTENSIONS'])
        eq_('', ctx['ZEND_EXTENSIONS'])

    def test_convert_php_extensions_54_one(self):
        ctx = {
            'PHP_VERSION': '5.4.x',
            'PHP_EXTENSIONS': ['mod1'],
            'ZEND_EXTENSIONS': ['zmod1']
        }
        convert_php_extensions(ctx)
        eq_('extension=mod1.so', ctx['PHP_EXTENSIONS'])
        eq_('zend_extension="@HOME/php/lib/php/extensions/'
            'no-debug-non-zts-20100525/zmod1.so"',
            ctx['ZEND_EXTENSIONS'])

    def test_convert_php_extensions_55_one(self):
        ctx = {
            'PHP_VERSION': '5.5.x',
            'PHP_EXTENSIONS': ['mod1'],
            'ZEND_EXTENSIONS': ['zmod1']
        }
        convert_php_extensions(ctx)
        eq_('extension=mod1.so', ctx['PHP_EXTENSIONS'])
        eq_('zend_extension="zmod1.so"',
            ctx['ZEND_EXTENSIONS'])

    def test_build_php_environment(self):
        ctx = {}
        build_php_environment(ctx)
        eq_(True, 'PHP_ENV' in ctx.keys())
        eq_(True, ctx['PHP_ENV'].find('env[HOME]') >= 0)
        eq_(True, ctx['PHP_ENV'].find('env[PATH]') >= 0)

    def test_is_web_app(self):
        ctx = {}
        eq_(True, is_web_app(ctx))
        ctx['WEB_SERVER'] = 'nginx'
        eq_(True, is_web_app(ctx))
        ctx['WEB_SERVER'] = 'httpd'
        eq_(True, is_web_app(ctx))
        ctx['WEB_SERVER'] = 'none'
        eq_(False, is_web_app(ctx))

    def test_find_stand_alone_app_to_run_app_start_cmd(self):
        ctx = {'APP_START_CMD': "echo 'Hello World!'"}
        eq_("echo 'Hello World!'", find_stand_alone_app_to_run(ctx))
        results = ('app.php', 'main.php', 'run.php', 'start.php', 'app.php')
        for i, res in enumerate(results):
            ctx = {'BUILD_DIR': 'tests/data/standalone/test%d' % (i + 1)}
            eq_(res, find_stand_alone_app_to_run(ctx))

    def test_load_binary_index(self):
        ctx = {'BP_DIR': '.', 'STACK': 'lucid'}
        json = load_binary_index(ctx)
        assert json is not None
        assert 'php' in json.keys()
        eq_(6, len(json['php'].keys()))

    def test_find_all_php_versions(self):
        ctx = {'BP_DIR': '.', 'STACK': 'lucid'}
        json = load_binary_index(ctx)
        versions = find_all_php_versions(json)
        eq_(6, len(versions))
        eq_(3, len([v for v in versions if v.startswith('5.4.')]))
        eq_(3, len([v for v in versions if v.startswith('5.5.')]))

    def test_find_php_extensions(self):
        ctx = {'BP_DIR': '.', 'STACK': 'lucid'}
        json = load_binary_index(ctx)
        exts = find_all_php_extensions(json)
        eq_(6, len(exts.keys()))
        tmp = exts[exts.keys()[0]]
        assert 'amqp' in tmp
        assert 'apc' in tmp
        assert 'imap' in tmp
        assert 'ldap' in tmp
        assert 'phalcon' in tmp
        assert 'pspell' in tmp
        assert 'pdo_pgsql' in tmp
        assert 'mailparse' in tmp
        assert 'redis' in tmp
        assert 'pgsql' in tmp
        assert 'snmp' in tmp
        assert 'cgi' not in tmp
        assert 'cli' not in tmp
        assert 'fpm' not in tmp
        assert 'pear' not in tmp

    def test_validate_php_version(self):
        ctx = {
            'ALL_PHP_VERSIONS': ['5.4.31', '5.4.30'],
            'PHP_54_LATEST': '5.4.31',
            'PHP_VERSION': '5.4.30'
        }
        validate_php_version(ctx)
        eq_('5.4.30', ctx['PHP_VERSION'])
        ctx['PHP_VERSION'] = '5.4.29'
        validate_php_version(ctx)
        eq_('5.4.31', ctx['PHP_VERSION'])
        ctx['PHP_VERSION'] = '5.4.30'
        validate_php_version(ctx)
        eq_('5.4.30', ctx['PHP_VERSION'])

    def test_validate_php_extensions(self):
        ctx = {
            'ALL_PHP_EXTENSIONS': {
                '5.4.31': ['curl', 'pgsql', 'snmp', 'phalcon']
            },
            'PHP_VERSION': '5.4.31',
            'PHP_EXTENSIONS': ['curl', 'snmp']
        }
        validate_php_extensions(ctx)
        eq_(2, len(ctx['PHP_EXTENSIONS']))
        assert 'curl' in ctx['PHP_EXTENSIONS']
        assert 'snmp' in ctx['PHP_EXTENSIONS']
        ctx['PHP_EXTENSIONS'] = ['curl', 'pspell', 'imap', 'phalcon']
        validate_php_extensions(ctx)
        eq_(2, len(ctx['PHP_EXTENSIONS']))
        assert 'curl' in ctx['PHP_EXTENSIONS']
        assert 'phalcon' in ctx['PHP_EXTENSIONS']
