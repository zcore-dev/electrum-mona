Electrum-mona - Lightweight Monacoin client
=====================================

::

  Licence: MIT Licence
  Author: Thomas Voegtlin
  Port Maintainer: WakiyamaP (Electrum-mona)
  Language: Python (>= 3.6)
  Homepage: https://electrum-mona.org/


.. image:: https://travis-ci.org/wakiyamap/electrum-mona.svg?branch=master
    :target: https://travis-ci.org/wakiyamap/electrum-mona
    :alt: Build Status
.. image:: https://coveralls.io/repos/github/wakiyamap/electrum-mona/badge.svg?branch=master
    :target: https://coveralls.io/github/wakiyamap/electrum-mona?branch=master
    :alt: Test coverage statistics





Getting started
===============

Electrum-mona is a pure python application. If you want to use the
Qt interface, install the Qt dependencies::

    sudo apt-get install python3-pyqt5

If you downloaded the official package (tar.gz), you can run

Electrum-mona from its root directory without installing it on your
system; all the python dependencies are included in the 'packages'
directory. To run Electrum-mona from its root directory, just do::

    ./run_electrum

You can also install Electrum-mona on your system, by running this command::

    sudo apt-get install python3-setuptools
    python3 -m pip install .[fast]

This will download and install the Python dependencies used by
Electrum-mona instead of using the 'packages' directory.
The 'fast' extra contains some optional dependencies that we think
are often useful but they are not strictly needed.

If you cloned the git repository, you need to compile extra files
before you can run Electrum-mona. Read the next section, "Development
Version".



Development version
===================

Check out the code from GitHub::

    git clone https://github.com/wakiyamap/electrum-mona.git
    cd electrum-mona
    git submodule update --init

Need lyra2rev2_hash::

    pip3 install lyra2re2-hash

Run install (this should install dependencies)::

    python3 -m pip install .[fast]

Compile the protobuf description file::

    sudo apt-get install protobuf-compiler
    protoc --proto_path=electrum_mona --python_out=electrum_mona electrum_mona/paymentrequest.proto

Create translations (optional)::

    sudo apt-get install python-requests gettext
    ./contrib/pull_locale




Creating Binaries
=================

Linux (tarball)
---------------

See :code:`contrib/build-linux/README.md`.


Linux (AppImage)
----------------

See :code:`contrib/build-linux/appimage/README.md`.


Mac OS X / macOS
----------------

See :code:`contrib/osx/README.md`.


Windows
-------

See :code:`contrib/build-wine/README.md`.


Android
-------

See :code:`electrum_mona/gui/kivy/Readme.md`.
