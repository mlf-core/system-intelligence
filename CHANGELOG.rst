==========
Changelog
==========

This project adheres to `Semantic Versioning <https://semver.org/>`_.


2.0.2 (2021-01-24)
------------------

**Added**

**Fixed**

**Dependencies**

* less strict pin of rich and click

**Deprecated**


2.0.1 (2021-01-03)
------------------

**Added**

* Updated documentation

* Updated PyPi classifiers

**Fixed**

**Dependencies**

**Deprecated**


2.0.0 (2021-01-03)
------------------

**Added**

* Complete support for MacOS
* Complete support for Windows
* Modelname query for MacOS
* Python 3.9 WFs for all GitHub Actions
* Run system-intelligence WF after build
* Multiple comments and docstrings
* Redesigned code structure to more OOP concept
* RAM memory attributes will now be displayed in Bytes (was Hertz)

**Fixed**

* Accelerated software query (about 5 times faster now)
* Fixed a bug that causes SI to crash and not generate a html report
  when path given via cli option was different to the cwd

**Dependencies**

* plistlib (from std lib)

**Deprecated**

* Unit-util file (most functions are now part of the base info class)


1.2.4 (2020-08-20)
------------------

**Added**

* Richified all prints

**Fixed**

**Dependencies**

**Deprecated**


1.2.3 (2020-08-18)
------------------

**Added**

* mkl to supported software to query for

**Fixed**

* Python dependency version handling

**Dependencies**

**Deprecated**


1.2.2 (2020-07-06)
------------------

**Added**

**Fixed**

* cpu cache raw_level is now always a string (fixes py-cpuinfo 7.0.0 returning integers)
* Replaced gif with full size gif

**Dependencies**

**Deprecated**


1.2.1 (2020-06-25)
------------------

**Added**

**Fixed**

* Import error if pycuda is not available

**Dependencies**

**Deprecated**


1.2.0 (2020-06-24)
------------------

**Added**

* html table output via --generate_html_table

**Fixed**

**Dependencies**

**Deprecated**


1.1.0 (2020-06-23)
------------------

**Added**

* Python packages to stdout

**Fixed**

* nvcc version is now correctly reported

**Dependencies**

**Deprecated**


1.0.0 (2020-06-23)
------------------

**Added**

* Scopes all, Hostname, OS, CPU, GPUs, RAM, HDDs, Network and Software
* saving to raw, json, yml
* rich stdout

**Fixed**

**Dependencies**

**Deprecated**
