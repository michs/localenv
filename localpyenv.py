#!/usr/bin/env python
"""
Create local working environments for Python.
"""

import ConfigParser
import optparse
import os
import site
import stat
import sys
import types

EXTRA_SITE_PACKAGES = False
SYSTEM_SITE_PACKAGES = False
USER_SITE_PACKAGES = False


def process_commandline():
    global EXTRA_SITE_PACKAGES, SYSTEM_SITE_PACKAGES, USER_SITE_PACKAGES

    parser = optparse.OptionParser(usage="%prog [options] directory")
    parser.add_option(
        '-s',
        '--system-site-packages',
        dest="system_site_packages",
        action="store_true",
        default=False,
        help="Make system site packages available.")
    parser.add_option(
        '-u',
        '--user-site-packages',
        dest="user_site_packages",
        action="store_true",
        default=False,
        help="Make user site packages available.")
    options, args = parser.parse_args()
    SYSTEM_SITE_PACKAGES = options.system_site_packages
    USER_SITE_PACKAGES = options.user_site_packages
    if len(args) != 1:
        print >>sys.stderr, "Error: Only the environment directory should be specified"
        return None
    return args[0]

def create_envscripts(path):
    success = False
    if os.system("mkdir -p %s/bin" % (path,)) == 0:
        os.chdir(path)
        fp = open("bin/activate.sh", "w")
        print >>fp, "ENV_ROOT=%s" % (path,)
        print >>fp
        print >>fp, activate_script
        fp.close()

        fp = open("bin/create_environment.sh", "w")
        print >>fp, "#!/bin/bash"
        print >>fp, "ENV_ROOT=%s" % (path,)
        print >>fp
        print >>fp, "PY_SYSPREFIX=%s" % (sys.prefix,)
        print >>fp, "PY_VERSION=%d.%d" % (sys.version_info.major, sys.version_info.minor)
        print >>fp, create_script
        if os.name == 'posix':
            os.fchmod(fp.fileno(), stat.S_IRWXU
                                   |stat.S_IRGRP|stat.S_IXGRP
                                   |stat.S_IROTH|stat.S_IXOTH)
        fp.close()
        success = True
    if not success:
        print >>sys.stderr, "Failed to create ", path
    return success

# def getsitepackages(userpackages):
#     ret = []
#     defpath = "%s/lib/python%s.%s" % (sys.prefix,
#                                       sys.version_info.major,
#                                       sys.version_info.minor)
#     for dir in sys.path:
#         if (not dir.startswith(defpath)
#             and not dir == os.path.dirname(sys.argv[0])
#             and not dir in userpackages):
#             ret.append(dir)
#     return ret

def ensure_list(arg):
    if type(arg) != types.ListType:
        if arg:
            arg =  [ arg ]
        else:
            arg = []
    return arg

def create_sitecustomize(path):
    extra_sitepacks = []
    sitepacks = ensure_list(site.getsitepackages())
    user_sitepacks = ensure_list(site.getusersitepackages())

    fp = open("bin/sitecustomize.py", "w")

    print >>fp, 'import os, site, sys'

    print >>fp, 'EXTRA_SITE_PACKAGES = ' + str(EXTRA_SITE_PACKAGES)
    print >>fp, 'SYSTEM_SITE_PACKAGES = ' + str(SYSTEM_SITE_PACKAGES)
    print >>fp, 'USER_SITE_PACKAGES = ' + str(USER_SITE_PACKAGES)

    if extra_sitepacks:
        print >>fp, 'extra_sitepacks = ["' + '", "'.join(extra_sitepacks) + '"]'
    else:
        print >>fp, 'extra_sitepacks = [ ]'
    if sitepacks:
        print >>fp, 'sitepacks = ["' + '", "'.join(sitepacks) + '"]'
    else:
        print >>fp, 'sitepacks = [ ]'
    if user_sitepacks:
        print >>fp, 'user_sitepacks = ["' + '", "'.join(user_sitepacks) + '"]'
    else:
        print >>fp, 'user_sitepacks = [ ]'

    print >>fp, site_script

    fp.close()

# Body for "bin/activate.sh"
activate_script = """
deactivate () {
    # reset old environment variables
    if [ -n "$_OLDENV_PATH" ] ; then
        PATH="$_OLDENV_PATH"
        export PATH
        unset _OLDENV_PATH
    fi
    if [ -n "$_OLDENV_PYTHONHOME" ] ; then
        PYTHONHOME="$_OLDENV_PYTHONHOME"
        export PYTHONHOME
        unset _OLDENV_PYTHONHOME
    else
        unset PYTHONHOME
    fi

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "$BASH" -o -n "$ZSH_VERSION" ] ; then
        hash -r 2>/dev/null
    fi

    if [ -n "$_OLDENV_PS1" ] ; then
        PS1="$_OLDENV_PS1"
        export PS1
        unset _OLDENV_PS1
    fi

    unset NONVIRTUAL_ENV
    if [ ! "$1" == "nondestructive" ] ; then
        # Self destruct!
        unset -f deactivate
    fi
}

_OLDENV_PATH="$PATH"
export PATH="${ENV_ROOT}/bin:$PATH"

if [ -n "${PYTHONHOME}" ] ; then
    _OLDENV_PYTHONHOME="${PYTHONHOME}"
    unset PYTHONHOME
fi
export PYTHONHOME="${ENV_ROOT}"

_OLDENV_PS1="$PS1"
export PS1="($(basename ${ENV_ROOT})) ${PS1}"
"""

# Body for "bin/create_environment.sh"
create_script = """
mkdir -p ${ENV_ROOT}/lib/python${PY_VERSION}/site-packages
mkdir -p ${ENV_ROOT}/include

find ${PY_SYSPREFIX}/bin -maxdepth 1 \\
         -name python\* \\
         -exec ln -fns {} ${ENV_ROOT}/bin \;

find ${PY_SYSPREFIX}/include -maxdepth 1 \\
         -exec ln -fns {} ${ENV_ROOT}/include \;

find ${PY_SYSPREFIX}/lib -maxdepth 1 \\
         \! -name python${PY_VERSION} \\
         -exec ln -fns {} ${ENV_ROOT}/lib \;

find ${PY_SYSPREFIX}/lib/python${PY_VERSION} -maxdepth 1 \\
         \! -name site-packages \! -name sitecustomize.\*  \\
         -exec ln -fns {} ${ENV_ROOT}/lib/python${PY_VERSION} \;

ln -s ${ENV_ROOT}/bin/sitecustomize.py ${ENV_ROOT}/lib/python${PY_VERSION}
"""

# Body for "bin/sitecustomize.py"
site_script = """
def list_remove(l, dir):
    i = 0
    while i < len(l):
        if l[i].startswith(dir):
            l.remove(l[i])
        else:
            i = i + 1

for dir in extra_sitepacks+sitepacks+user_sitepacks:
    list_remove(sys.path, dir)

if USER_SITE_PACKAGES:
    for dir in user_sitepacks:
        site.addsitedir(dir)
if SYSTEM_SITE_PACKAGES:
    for dir in sitepacks:
        site.addsitedir(dir)
if EXTRA_SITE_PACKAGES:
    for dir in user_sitepacks:
        site.addsitedir(dir)
"""

if __name__ == '__main__':
    path = process_commandline()
    if path:
        path = os.path.abspath(path)
        create_envscripts(path)
        create_sitecustomize(path)
