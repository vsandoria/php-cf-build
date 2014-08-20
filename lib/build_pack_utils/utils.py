import os
import shutil
import imp
import logging
from string import Template


_log = logging.getLogger('utils')


def safe_makedirs(path):
    try:
        os.makedirs(path)
    except OSError, e:
        # Ignore if it exists
        if e.errno != 17:
            raise e


def load_env(path):
    _log.info("Loading environment from [%s]", path)
    env = {}
    with open(path, 'rt') as envFile:
        for line in envFile:
            name, val = line.strip().split('=', 1)
            env[name.strip()] = val.strip()
    _log.debug("Loaded environment [%s]", env)
    return env


def load_processes(path):
    _log.info("Loading processes from [%s]", path)
    procs = {}
    with open(path, 'rt') as procFile:
        for line in procFile:
            name, cmd = line.strip().split(':', 1)
            procs[name.strip()] = cmd.strip()
    _log.debug("Loaded processes [%s]", procs)
    return procs


def load_extension(path):
    _log.debug("Loading extension from [%s]", path)
    info = imp.find_module('extension', [path])
    return imp.load_module('extension', *info)


def process_extension(path, ctx, to_call, success, args=None, ignore=False):
    _log.debug('Processing extension from [%s] with method [%s]',
               path, to_call)
    if not args:
        args = [ctx]
    extn = load_extension(path)
    try:
        if hasattr(extn, to_call):
            success(getattr(extn, to_call)(*args))
    except Exception:
        _log.exception("Error with extension [%s]" % path)
        if not ignore:
            raise


def process_extensions(ctx, to_call, success, args=None, ignore=False):
    for path in ctx['EXTENSIONS']:
        process_extension(path, ctx, to_call, success, args, ignore)


def rewrite_with_template(template, cfgPath, ctx):
    with open(cfgPath) as fin:
        data = fin.read()
    with open(cfgPath, 'wt') as out:
        out.write(template(data).safe_substitute(ctx))


def rewrite_cfgs(toPath, ctx, delim='#'):
    class RewriteTemplate(Template):
        delimiter = delim
    if os.path.isdir(toPath):
        _log.info("Rewriting configuration under [%s]", toPath)
        for root, dirs, files in os.walk(toPath):
            for f in files:
                cfgPath = os.path.join(root, f)
                _log.debug("Rewriting [%s]", cfgPath)
                rewrite_with_template(RewriteTemplate, cfgPath, ctx)
    else:
        _log.info("Rewriting configuration file [%s]", toPath)
        rewrite_with_template(RewriteTemplate, toPath, ctx)


class FormattedDictWrapper(object):
    def __init__(self, obj):
        self.obj = obj

    def unwrap(self):
        return self.obj


def wrap(obj):
    return FormattedDictWrapper(obj)


class FormattedDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def format(self, val):
        if hasattr(val, 'format'):
            val = val.format(**self)
            newVal = val.format(**self)
            while val != newVal:
                val = newVal
                newVal = newVal.format(**self)
            return val
        if hasattr(val, 'unwrap'):
            return val.unwrap()
        return val

    def __getitem__(self, key):
        return self.format(dict.__getitem__(self, key))

    def get(self, *args, **kwargs):
        if kwargs.get('format', True):
            return self.format(dict.get(self, *args))
        else:
            return dict.get(self, *args)


# This is copytree from PyPy 2.7 source code.
#   https://bitbucket.org/pypy/pypy/src/9d88b4875d6e/lib-python/2.7/shutil.py
# Modifying this so that it doesn't care about an initial directory existing
def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().

    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()
    try:
        os.makedirs(dst)
    except OSError, e:
        if e.errno != 17:  # File exists
            raise e
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors
