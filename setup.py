#!/usr/bin/env python

import os
import sys
from glob import glob

sys.path.insert(0, os.path.abspath('lib'))
from ansible import __version__, __author__
try:
    from setuptools import setup, find_packages
except ImportError:
    print "Ansible now needs setuptools in order to build. " \
          "Install it using your package manager (usually python-setuptools) or via pip (pip install setuptools)."
    sys.exit(1)

this_dir = os.path.dirname(__file__)
if os.path.exists(os.path.join(this_dir, '.gitmodules')) and not os.path.exists(os.path.join(this_dir, '.git')):
    import ConfigParser
    import shutil
    import StringIO
    import urllib
    import zipfile
    import ansible.modules
    for submodule in ('core', 'extras'):
        try:
            __import__('ansible.modules.%s' % submodule)
        except ImportError:
            print('Unable to find %s modules, attempting to find submodule URL.' % submodule)
            sub_path = os.path.join(os.path.dirname(ansible.modules.__file__), submodule)
            rel_path = os.path.relpath(sub_path, this_dir)
            cp = ConfigParser.SafeConfigParser()
            gm = open(os.path.join(this_dir, '.gitmodules')).read()
            gm = '\n'.join([x.strip() for x in gm.splitlines()])
            fp = StringIO.StringIO(gm)
            cp.readfp(fp)
            for section in cp.sections():
                try:
                    sm_path = cp.get(section, 'path')
                    if sm_path != rel_path:
                        continue
                    sm_url = cp.get(section, 'url')
                    sm_branch = cp.get(section, 'branch')
                except ConfigParser.Error:
                    continue
                sm_url = sm_url.replace('.git', '/archive/%s.zip' % sm_branch)
                print('Downloading %s modules from %s' % (submodule, sm_url))
                zf_path, _ = urllib.urlretrieve(sm_url)
                try:
                    with zipfile.ZipFile(zf_path) as zf:
                        for name in zf.namelist():
                            parts = [sub_path] + name.split(os.sep)[1:]
                            dest_name = os.path.join(*parts)
                            print('Extracting %s to %s' % (name, dest_name))
                            if name.endswith('/'):
                                if not os.path.isdir(dest_name):
                                    os.makedirs(dest_name)
                            else:
                                with zf.open(name) as zfobj:
                                    with open(dest_name, 'w') as dfobj:
                                        shutil.copyfileobj(zfobj, dfobj)
                finally:
                    os.unlink(zf_path)
                try:
                    __import__('ansible.modules.%s' % submodule)
                    print('Successfully added %s modules' % submodule)
                    break
                except ImportError:
                    print('Something went wrong, still cannot find %s modules' % submodule)
                    sys.exit(1)

setup(name='ansible',
      version=__version__,
      description='Radically simple IT automation',
      author=__author__,
      author_email='michael@ansible.com',
      url='http://ansible.com/',
      license='GPLv3',
      install_requires=['paramiko', 'jinja2', "PyYAML", 'setuptools', 'pycrypto >= 2.6'],
      package_dir={ 'ansible': 'lib/ansible' },
      packages=find_packages('lib'),
      package_data={
         '': ['module_utils/*.ps1', 'modules/core/windows/*.ps1', 'modules/extras/windows/*.ps1'],
      },
      scripts=[
         'bin/ansible',
         'bin/ansible-playbook',
         'bin/ansible-pull',
         'bin/ansible-doc',
         'bin/ansible-galaxy',
         'bin/ansible-vault',
      ],
      data_files=[],
)
