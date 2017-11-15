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

``jasmin_arc`` also requires the ARC client Python library to installed; follow the instructions
relevant to your OS `here <#>`_. (**TODO**: find some instructions!)

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

To run the tests, use:

.. code-block:: bash

   python tests/tests.py

Documentation
-------------

Code is documented inline using `Sphinx`_. To generate the documentation as HTML

.. _Sphinx: http://www.sphinx-doc.org/en/stable/

.. code-block:: bash

   cd doc
   make html

This will create HTML files in ``build/html``

