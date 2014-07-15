#!/usr/bin/python

# Released under the New BSD licence:

# Copyright (c) 2011 Massachusetts Institute of Technology.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Massachusetts Institute of Technology nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""Attempts to package an executable .py script along with the
non-system modules that it imports. See:

http://evanjones.ca/software/packagepy.html
"""

__author__ = "Evan Jones <evanj@csail.mit.edu>"

import modulefinder
import os
import sys
import zipfile


def notBuiltInModules(script_path):
    """Returns a list of (module, path) pairs that are not built-in modules."""
    # Figure out the paths for "built-in" modules:
    # Remove any paths in PYTHONPATH, as those are clearly not "built-in"
    # sys.path[0] is the "script path": ignore it
    pythonpaths = set({})
    if "PYTHONPATH" in os.environ:
        for path in os.environ["PYTHONPATH"].split(os.pathsep):
            pythonpaths.add(path)
    system_paths = []
    for p in sys.path[1:]:
        # RAY: this is a hack to detect system paths, had to patch this
        if p not in pythonpaths and 'site-packages' not in p:
            system_paths.append(p)
    # print "system paths:", "; ".join(system_paths)

    finder = modulefinder.ModuleFinder()
    finder.run_script(script_path)
    #~ finder.report()

    not_builtin = []
    for name, module in finder.modules.iteritems():
        # The _bisect module has __file__ = None
        if not hasattr(module, "__file__") or module.__file__ is None:
            # Skip built-in modules
            #print 'skipping: ' + name 
            continue

        system_module = False
        for system_path in system_paths:
            if module.__file__.startswith(system_path):
                system_module = True
                #print 'system: ' + module.__file__
                break
        if system_module:
            continue

        # Skip the script
        if name == "__main__":
            assert module.__file__ == script_path
            continue

        if not module.__file__.endswith('.py'):
            print 'Skipping non-python file: ' + module.__file__
            continue

        relative_path = name.replace('.', '/')
        if module.__path__:
            #~ # This is a package; originally I skipped it, but that is not a good idea
            assert module.__file__.endswith("/__init__.py")
            relative_path += "/__init__.py"
        else:
            relative_path += os.path.splitext(module.__file__)[1]

        assert name != "__main__"
        not_builtin.append((module.__file__, relative_path))
    return not_builtin


def main(script_path, output_path):
    if os.path.exists(output_path):
        sys.stderr.write("output path '%s' exists; refusing to overwrite\n" % output_path)
        return 1

    not_builtin = notBuiltInModules(script_path)

    if len(not_builtin) == 0:
        sys.stderr.write("No modules found that are not built-in; doing nothing (bug?)\n")
        return 1

    # We make a zip! We start with a Python header
    outfile = open(output_path, 'w+b')
    outfile.write("#!/usr/bin/env python\n")
    outfile.flush()

    outzip = zipfile.ZipFile(outfile, 'a', zipfile.ZIP_DEFLATED)
    #~ outzip = zipfile.ZipFile(output_path, 'a', zipfile.ZIP_DEFLATED)

    # TODO: Save compiled python (.pyc or .pyo) instead of source? Bytecode may
    # not be compatible between versions though?
    outzip.write(script_path, "__main__.py")

    # TODO generalize this to commandline args
    # hack to explicitly add boto/endpoints.json
    boto = __import__('boto', globals(), locals(), [], -1)
    not_builtin.append((os.path.dirname(boto.__file__) + '/endpoints.json', 'boto/endpoints.json'))

    for source_path, relative_destination_path in not_builtin:
        outzip.write(source_path, relative_destination_path)
    outzip.close()

    os.chmod(output_path, 0755)

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("packagepy.py (script to package) (package output)\n")
        sys.exit(1)
    script_path = sys.argv[1]
    output_path = sys.argv[2]

    main(script_path, output_path)
    sys.exit(0)

