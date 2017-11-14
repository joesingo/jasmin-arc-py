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

``jasmin_arc`` also requires the ARC client Python library to installed; follow the instructions
relevant to your OS `here <#>`_. (**TODO**: find some instructions!)

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
The required options are:

* ``pem_file``: **Description here** (default: ``~/.arc/userkey-nopass.pem``)

* ``client_cert_file``: **Description here** (default: ``~/.arc/usercert.pem``)

* ``browser_cert_file``: **Description here** (default: ``~/certBundle.p12``)

* ``certs_dir``: **Description here** (default: ``/etc/grid-security/certificates``)

* ``arc_proxy_cmd``: **Description here** (default: ``/usr/bin/arcproxy``)

* ``myproxy_file``: **Description here** (default: ``/tmp/x509up_u502``)

* ``arc_server``: URL to the ARC server (default: ``jasmin-ce.ceda.ac.uk:60000/arex``)

* ``outputs_filename``: The name of the file that will be retrieved when saving job outputs. This
  should match the location output is written to in your job scripts. (default: ``outputs.zip``)

* ``errors_filename``: Similar to ``outputs_filename`` but for error output. (default: ``errors_file.txt``)

``ArcInterface`` class
----------------------

.. automodule:: jasmin_arc.jasmin_arc
    :members:
    :undoc-members:
    :noindex:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
