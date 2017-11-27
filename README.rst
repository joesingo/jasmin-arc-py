jasmin-arc-py
=============

``jasmin_arc`` is a Python library to facilitate running jobs on LOTUS_ on JASMIN via the
ARC-CE server.

.. _LOTUS: http://jasmin.ac.uk/services/lotus/

To get started, obtain the necessary certificates by following the instructions
`here <http://help.ceda.ac.uk/article/4502-setting-up-certificates>`_.

See the `help pages <http://help.ceda.ac.uk/category/4500-arc-ce-on-jasmin>`_ for more information
about using ARC-CE on JASMIN.

Installation
============

Use ``pip`` for installation:

.. code-block:: bash

   git clone https://github.com/cedadev/jasmin-arc-py.git
   cd jasmin-arc-py
   pip install .

Alternatively, to install straight from GitHub:

.. code-block:: bash

   pip install git+https://github.com/cedadev/jasmin-arc-py

``jasmin_arc`` also requires the ARC client Python library to installed. On CentOS 6:

.. code-block:: bash

   # Remove the epel cache if any:
   rm -rf /var/cache/yum/x86_64/6/epel
   rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
   rpm -Uvh  http://download.nordugrid.org/packages/nordugrid-release/releases/15.03/centos/el6/x86_64/nordugrid-release-15.03-1.el6.noarch.rpm
   yum update
   yum install  nordugrid-arc-client-tools
   # Check installation:
   arcinfo --version

On Ubuntu:

.. code-block:: bash

   wget -q http://download.nordugrid.org/DEB-GPG-KEY-nordugrid.asc -O- | sudo apt-key add -
   apt-get update
   apt-get install nordugrid-arc-python
   apt-get install globus-gsi-cert-utils-progs

If working in a virtual enviroment you may also need to add the location of the ARC installation to
your ``PYTHONPATH``:

.. code-block:: bash

   export PYTHONPATH=/usr/lib64/python2.6/site-packages:$PYTHONPATH

The location of your ARC installation may be different from the example given here.

For complete documentation and usage, see the the documentation on `read the docs`_.

.. _read the docs: http://jasmin-arc-py.readthedocs.io/en/latest/

Development
===========

To install any dependencies required for testing or building documentation, use:

.. code-block:: bash

   pip install -r requirements.txt

Tests
-----

To run the tests, set the ``JASMIN_ARC_CONFIG`` environmental variable to specify the credentials
to use use in the tests:

.. code-block:: bash

   export JASMIN_ARC_CONFIG=/path/to/config

Then run:

.. code-block:: bash

   python tests/tests.py

There are also some test that require some manual input, such as logging into JASMIN and checking
the status of a job with ``bjobs -a``. To run these tests use:

.. code-block:: bash

   python tests/manual_tests.py

If ARC jobs do not run under the same user as you log in to JASMIN with, use ``bjobs -u <user> -a``
instead.

Documentation
-------------

Code is documented inline using `Sphinx`_. To generate the documentation as HTML

.. _Sphinx: http://www.sphinx-doc.org/en/stable/

.. code-block:: bash

   cd doc
   make html

This will create HTML files in ``build/html``.

When creating, renaming or deleting source files, use ``sphinx-apidoc`` to generate the module index pages:

.. code-block:: bash

   cd doc/source
   rm jasmin_arc.rst modules.rst  # Delete existing index pages
   sphinx-apidoc -o . ../../jasmin_arc

Remember to commit these files in git afterwards.

