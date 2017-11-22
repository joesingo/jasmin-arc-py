.. jasmin-arc-py documentation master file, created by
   sphinx-quickstart on Mon Nov 13 10:44:32 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to jasmin-arc-py's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

``jasmin_arc`` is a Python library to facilitate running jobs on LOTUS_ on JASMIN via the
ARC-CE server.

.. _LOTUS: http://jasmin.ac.uk/services/lotus/

To get started, obtain the necessary certificates by following the instructions
`here <http://help.ceda.ac.uk/article/4502-setting-up-certificates>`_.

.. hint::
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

.. note:: The location of your ARC installation may be different from the example given here.

API Usage
=========

Some introductory text about the API here (quickstart guide?)

Configuration
-------------

``jasmin_arc`` uses a JSON file to configure the connection to the ARC CE server.
The required options and default values are defined in the :class:`ConnectionConfig` class:

.. autoclass:: jasmin_arc.config.ConnectionConfig
   :members:

For any options not included in the JSON config, the default values shown above will be used.
For example, to use the default options except for the path to your private key and the ARC
server URL, use the following JSON:

.. code-block:: json

   {
     "PEM_FILE": "/my/private/key",
     "ARC_SERVER": "my-arc-server.ac.uk"
   }

``ArcInterface`` class
----------------------

.. automodule:: jasmin_arc.arc_interface
    :members:
    :undoc-members:
    :noindex:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
