
.. _python-versioning:

==============================================
Python's Versioning and Stability Expectations
==============================================


Python Versions
===============

The Python language is developed together with its reference
:ref:`implementation <implementations>`, *CPython*.  Both share the same
release schedule and versioning scheme.

Production-ready Python versions numbered with three numbers,
``major.minor.micro``.

* New *major* versions are exceptional, and are planned very long in advance.
* New *minor* versions are feature releases; they get released annually.
* New *micro* versions are *bugfix* releases, which get released roughly
  every 2 months for 5 years after a minor release; or *security* releases
  which are made irregularly afterwards.

We also publish non-final *pre-release* versions with an additional
qualifier: *Alpha* (``a``), *Beta* (``b``) and *release candidates* (``rc``).
These versions are not production use; they're aimed at testers and maintainers
of third-party libraries.

The version number is combined into a single string, for example:

   +----------------------+-------+-------+-------+----------------------------+
   | Version              | Major | Minor | Micro | Prerelease                 |
   +======================+=======+=======+=======+============================+
   | Python ``3.6.3``     | 3     | 6     | 3     | Final (production-ready)   |
   +----------------------+-------+-------+-------+----------------------------+
   | Python ``3.7.0a3``   | 3     | 7     | 0     | Third *alpha*              |
   +----------------------+-------+-------+-------+----------------------------+
   | Python ``3.9.4b1``   | 3     | 9     | 4     | First *beta*               |
   +----------------------+-------+-------+-------+----------------------------+
   | Python ``2.7.14rc2`` | 2     | 7     | 14    | Second *release candidate* |
   +----------------------+-------+-------+-------+----------------------------+

When discussing features that do not change in *micro* or *minor* releases,
or ones that are new in `x.y.0` or `x.0.0` versions,
it is common to only specify the relevant numbers:

   +-----------------+-------+-------+-------+
   | Version         | Major | Minor | Micro |
   +=================+=======+=======+=======+
   | Python ``3.10`` | 3     | 10    | any   |
   +-----------------+-------+-------+-------+
   | Python ``3``    | 3     | any   | any   |
   +-----------------+-------+-------+-------+


See also the documentation for :data:`sys.version_info`,
:data:`sys.hexversion`, :data:`sys.version`, and :ref:`apiabiversion`,
which expose version numbers in different formats.


.. _python-releases:

Python Releases
===============

All releases, including pre-releases, are available
from https://www.python.org/downloads/.  New releases are announced on the
comp.lang.python and comp.lang.python.announce newsgroups and on the Python
home page at `python.org`_; an RSS feed of news is available.

.. _python.org: https://python.org


.. _python-stability:

Versioning details and Stability Expectations
=============================================

This section documents stability expectations for the various types of Python
releases. It is intended for users of Python, that is, general programmers
and library maintainers.

For developers *of* Python, this topic is covered in the
`Development Cycle`_ section of the devguide and in :pep:`387` --
*Backwards Compatibility Policy*.

The *schedules* for specific minor-version releases are covered in the
`Status of Python branches`_ and `End-of-life branches`_ sections
of the devguide, where they're updated regularly.

For details on stability of Python's C API, see :ref:`stable`.

.. note::

   The “stability expectations” covered here are *goals*.
   Sometimes, Python will contain bugs in the form of unintentional
   backwards incompatible changes.
   Sometimes, a carefully considered exception to the rules is made.

   Python relies on people testing with pre-releases and
   reporting issues to find edge cases of backwards incompatibilities:
   if backwards compatibility is important to you, consider testing
   your codebase with Python pre-releases.

.. _Development Cycle: https://devguide.python.org/devcycle/#devcycle
.. _Status of Python branches: https://devguide.python.org/#status-of-python-branches
.. _End-of-life branches: https://devguide.python.org/devcycle/#end-of-life-branches


Major Versions
--------------

When Python 3.0.0 was released, most programs for Python 2 needed to be
adjusted for compatibility.  The transition took several decades.

There are currently no plans to release Python 4.  The expectation is that
the transition to Python 4.0, if and when it happens, will be similar to
the transition to a new minor version.


Minor Versions
--------------

Minor versions usually contain many new features and bugfixes.
All changes are collected in a :ref:`What's New <whatsnew-index>` document.

A new minor release may not be fully compatible with its predecessor.
Incompatibilities -- changes that make preexisting code cease to comparatively
function -- are generally only made after a *deprecation period*: code whose
behavior will change will emit :exc:`DeprecationWarning` for at least two
minor releases before being removed.
However, in extreme cases (e.g. for dangerously broken or insecure features)
the deprecation period may be skipped.

In new minor versions, Python may remove support for little-used platforms.
See :pep:`11` for more details and the process to get a platform re-supported.

.. note::
   Despite similarities, Python does not use the popular `semantic versioning`_
   scheme, which was published several decades after Python.

.. _semantic versioning: https://semver.org/


Micro Versions
--------------

A new micro version marks *bugfix* and *security* releases.
These releases are managed for stability; only fixes for known problems are
included in them, and Python's interfaces do not change in new micro versions.

Generally, it is enough for third-party libraries to test with one
release of a minor version -- ideally the latest one.
For example, a library tested with Python 3.5.10 may reasonably claim to be
compatible with Python 3.5 in general.


Bugfix Releases
...............

For about 18 months (1½ years) after a new minor version, *bugfix releases* are
made approximately every two months.
Bugfix releases contain sources and installers for Windows and macOS.

Backwards-incompatible changes are rare in bugfix releases, but sometimes
necessary for to fix serious bugs or to make Python work as documented.


Security Releases
.................

For forty two months (3½ years) after the bugfix period is over,
*security releases* are made on an as-needed basis (no fixed cadence).
For these, the micro version is incremented just like with bugfix releases.

Security releases only fix exploitable issues like crashes and possibilities
of privilege escalation.

Security releases are *source-only*: Windows and macOS installers for
them are not available from `python.org`_, which means that users of these
binaries should upgrade after the bugfix period ends.  (Other distributors
of Python will have their own support periods.)


End-of-life
...........

Five years after the initial release of a particular minor version,
a final security release is published and the minor version reaches
*End-of-life*.
No more changes at all are made to that minor version.


.. _python-prereleases:

Pre-releases
------------

Several months before a new minor version, and sometimes before a new micro
version, snapshots of the development branch are released as *pre-releases*.

Rough planned dates for pre-releases are recorded in Release Schedule PEPs,
as listed in the `Status of Python branches`_ section of the devguide.


Alpha versions
..............

Alpha versions give the community a chance to test a very early version
of the upcoming release and report any issues.
Most planned changes (such as removal of deprecated features) are done in
alpha releases.  Early new features are included as well, but additional
new features can be added to Python up until the first Beta release.

Alpha versions are unstable. (See Beta versions below for more details.)


Beta versions
.............

After the first Beta release, no new features are added, and development
focuses on fixing bugs and improving documentation.

Maintainers of third-party libraries are encouraged to test their code
with Beta releases, so any bugs or unforeseen issues can be resolved as early
as possible.

New features can be *removed* from the upcoming release in the Beta period.

Beta versions are unstable.
There are no backwards compatibility guarantees between beta versions.
For example, bytecode cache (`.pyc`) files may not be compatible and the
:ref:`ABI <stable>` for C-API extensions may still change.
Sharing :mod:`virtual environments <venv>` (and installed libraries in general)
between different beta versions is not a good idea.


Release Candidates
..................

The goal of Release Candidates (RCs) is to enable final testing and prepare the
wider Python ecosystem for the upcoming release.
Only serious bugs are fixed in RCs (aside from improvements to documentation
and internal tests).
Ideally, there would be no changes between a RC and the final release.

Release Candidates are *stable*;
the bar for changes in new RCs is higher than for new micro versions.
Third-party libraries that release for each minor version can and should
release in the RC period, so that users find the library
installable when the final version comes out.

For example, a build of `Numpy`_ for `3.10` can and should be published with
`3.10.0rc1`.  The changes between `3.10.0rc1` and `3.10.0` will be smaller
than between `3.10.0` and `3.10.1`.

.. _NumPy: https://numpy.org/


Unstable API
------------

The following are *not* considered stable, and may change at any time --
even in new micro versions (although that doesn't happen without a strong
reason):

* Anything (functions, classes, modules, attributes, methods, C-API names
  and types, etc.) with a name prefixed by "_", except
  :ref:`special names <specialnames>`).
* Anything documented publicly as being private.
* Imported modules (unless explicitly documented as part of the public API;
  e.g. if the ``spam`` module imports the ``bacon`` module, it does not
  automatically mean ``spam.bacon`` is part of the public API unless it is
  documented as such).
* Inheritance patterns of internal classes.
* Test suites. (Anything in the ``test`` package or ``test`` sub-packages.)
* API that is explicitly documented as :term:`provisional <provisional API>`.
* Features enabled by :ref:`future statements <future>`.
* The exact text and formatting of error messages and tracebacks.
* String representations of objects (results of ``str()`` and ``repr()``),
  unless documented.
* Exact types: any type may be replaced with a subtype
  (e.g. `FileNotFoundError` can be raised where `OSError` was raised
  previously).
* Exact output of parsing, serialization, compression, etc.
  For example, Zip, Pickle or ``*.pyc`` files produced from the same data
  may not be bit-by-bit identical, though they should be *functionally*
  identical.

All of these items will also often differ across
:ref:`implementations <implementations>` of the Python language.
Portable code should not rely on these details.

