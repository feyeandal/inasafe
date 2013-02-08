Running Tests
=============

To run a single test
--------------------

To run a single test it must be resolved as path to / file.py:Class.method -
for example::

    safe_qgis/test_dock.py:DockTest.test_runVolcanoCirclePopulation

Under OSX there is a helper script that will set up the appropriate paths::

    ./runtest-osx.sh safe_qgis/test_dock.py:DockTest.test_runVolcanoCirclePopulation

