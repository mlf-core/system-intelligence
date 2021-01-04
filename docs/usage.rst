=====
Usage
=====

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

As of version 2.0.0, you can also run queries by querying all scopes except for some of them.
An example, where one queries every scope except RAM and Software, would look like the following:

.. code-block:: console

    $ system-intelligence -e ram software

To suppress the standard output you may add the option

.. code-block:: console

    $ system_intelligence <scope> --silent


System-intelligence on MacOS
----------------------------
As with version 2.0.0, system-intelligence can also query under MacOS. However,
there are a few peculiarities:

1.) Querying host will also display the model marketing name of the users device (if available)

2.) As RAM info on MacOS is limited compared to Linux or Windows, the RAM query will only display
Slot, Type, Size, Speed and Serial Number of each RAM slot as well as the total memory size

3.) There is no need to run it with sudo, since it's not required like in Linux for example

4.) All memory size units (so every Byte unit) is displayed using base10, as this is 'Darwin's' way to compute such units

5.) The L1 Cache in the CPU query summarizes the L1i cache and the L1d cache together

System-intelligence on Windows
------------------------------
As with version 2.0.0, system-intelligence can also query under Windows. There are only a few minor things different to whats displayed under linux:

1.) L1 CPU cache size is not available (as for now) and thus will be not displayed

2.) Size units (bytes basically) are displayed using base2 computation as this is how Windows computes those numbers

Generate HTML report
--------------------
System-intelligence can not only print the results to stdout, but is also capable of creating nice HTML reports that can be included in your research or appliaction.
To generate such report in a file called result.html above the current working directory simply run the following:

.. code-block:: console

    $ system_intelligence all -f json -g -o result.html

Note, that under Windows, this must be:

.. code-block:: console

    $ system_intelligence all -f json -g -o result.html

Module
---------

To use system-intelligence in a project::

    import system_intelligence

To run queries you have to import

.. code-block:: python

    from system_intelligence.query import query_and_export

which will allow you to call the ``query_and_export`` function. Please note that it requires a list of a tuple as input.
This is pretty much a relict of the command line library Click.

.. code-block:: python

    query_and_export(query_scope=list(('all',)), verbose=True, export_format='json', generate_html_table=True, output='system_intelligence.json')::
