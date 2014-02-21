Localenv
========

Usage
-----
    As command:         localpyenv.py [options] directory
    As Python module:   python -m localpyenv [options] directory

    Options:
      -h, --help            show this help message and exit
      -s, --system-site-packages
                            Make system site packages available.
      -u, --user-site-packages
                            Make user site packages available.
        

Installation
------------
Place the script localpyenv.py either into a directory of the PATH or into one directory of Python's path.

Creation of a Python environment
--------------------------------

1. Initialize the environment
    localpyenv.py -s myenv

2. Link files from the used parent installation
    myenv/bin/create_environment.sh

Using a Python environment
--------------------------

In order to us a Python environment, source its activate script

    source myenv/bin/activate.sh

After the use, deactivate the environment

    deactivate


Rationale
---------
Developed in order to implement a few things in a different way than in [virtualenv](http://www.virtualenv.org).

* User site packages cannot be made available
* Recursive environments are not possible
* The used "site.py" differes from the one contained in Python 2.7
 + Different system site packages on platform 'darwin' appear with and without virtualenv
 + "site-python" cannot be inherited from the system installation
* Works with [Anaconda](https://store.continuum.io/cshop/anaconda/)
