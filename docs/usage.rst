=====
Usage
=====

To use system-intelligence in a project::

    import system_intelligence

command-line interface
----------------------------

To get an overview of system-intelligence run

.. code-block:: console

    $ system-intelligence --help

system-intelligence queries your system for hardware and software related information.
Available scopes are 'all', 'cpu', 'gpus', 'ram', 'host', 'os', 'hdd', 'swap', 'network', 'software'.
To query for your desired scope run

.. code-block:: console

    $ system-intelligence <scope> <optionally more scopes> ... <optionally more scopes>

If system-intelligence is run with scope 'all', all other scopes will be queried for.
Please note, that for GPU support you need to have `pycuda <https://documen.tician.de/pycuda/>`_ installed.
The installation instructions can be found `here <https://wiki.tiker.net/PyCuda/Installation/Linux/Ubuntu>`_.

To save all results into a file run

.. code-block:: console

    $ system-intelligence <scope> --output_format <raw/json/yml> --output <name_of_file.output_format>

As an example you may run

.. code-block:: console

    $ system-intelligence all --output_format json --output info.json

To suppress the standard output you may add the option

.. code-block:: console

    $ system_intelligence <scope> --silent
