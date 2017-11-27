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

It supports:

- Submitting jobs
- Uploading input files to be processed by jobs
- Retrieving job status
- Downloading job outputs
- Cancelling jobs

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

If working in a virtual environment you may also need to add the location of the ARC installation to
your ``PYTHONPATH``:

.. code-block:: bash

   export PYTHONPATH=/usr/lib64/python2.6/site-packages:$PYTHONPATH

.. note:: The location of your ARC installation may be different from the example given here.

API Usage
=========

Quickstart
----------

To get started, create a JSON config file that points to your private key and certificate
(see `Configuration`_ for the full list of config options):

.. code-block:: json

   {
     "CLIENT_KEY": "/path/to/private/key.pem",
     "CLIENT_CERT": "/path/to/cert.pem",
   }

All actions are performed through the `ArcInterface` class. A basic example is included below:

.. literalinclude:: examples/basic.py

See `Examples`_ for more examples.

API
---

`ArcInterface` contains methods for interacting with ARC on JASMIN. The most useful methods are
listed below:

.. autoclass:: jasmin_arc.arc_interface.ArcInterface
   :members: __init__, submit_job, get_job_status, save_job_outputs, cancel_job

Configuration
-------------

``jasmin_arc`` uses a JSON file to configure the connection to the ARC CE server.
The available options and default values are defined in the :class:`ConnectionConfig` class:

.. autoclass:: jasmin_arc.config.ConnectionConfig
   :members:
   :exclude-members: __init__

For any options not included in the JSON config, the default values shown above will be used.
For example, to use the default options except for the path to your private key and the ARC
server URL, use the following JSON:

.. code-block:: json

   {
     "CLIENT_KEY": "/my/private/key",
     "ARC_SERVER": "my-arc-server.ac.uk"
   }

Job input/output files
----------------------

Jobs submitted to LOTUS through ARC-CE are run from a *session directory* unique to each job. The
path to this directory will be something like
``/work/scratch/arc/grid/RmCMDmqK9brnMQPDjq2vDwNoABFKDmABFKDmvpFKDmWEFKDmnXLGem``, where the long
string of numbers at the end is the last component of the job ID.

.. note::

   You do not need to worry about the actual path to the session directory, as the current working
   directory will be set correctly when your jobs run.

Any input files passed to `ArcInterface.submit_job` are copied into this directory, and can be
accessed from your jobs.

Use the `OUTPUT_FILE` config option to specify which file/directory to download with
`ArcInterface.save_job_outputs`. This will download the specified file/directory, and also the
contents of ``stdout`` and ``stderr`` to ``stdout.txt`` and ``stderr.txt`` respectively.

Outputs are saved to a temporary directory (in ``/tmp`` on UNIX platforms), and the path
to this directory is returned. You may then move files to a more permanent location as required.

.. note::

   Any other files written to the session directory will be deleted when the job finishes.

Examples
--------

Setting log output destination and logging level:

.. literalinclude:: examples/logging.py

Uploading and processing input files:

.. literalinclude:: examples/input_files.py

Downloading output files

.. literalinclude:: examples/download_outputs.py

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
