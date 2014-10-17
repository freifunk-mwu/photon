
Photon Intro
------------

Photon is a backend utility for freifunk related scripts e.g. on gateways.

It could be best described as a **shell backend as python module**

The **/examples** directory contains some basic receipts on how to use Photon in your scripts.

Contributions are highly welcome [#contributions]_, also feel free to use the `issue tracker <http://github.com/spookey/photon/issues>`_ if you encounter any problems.

:Repository: `github.com/spookey/photon <http://github.com/spookey/photon/>`_
:Documentation: `photon.readthedocs.org <http://photon.readthedocs.org/en/latest/>`_
:Package: `pypi.python.org/pypi/photon_core <https://pypi.python.org/pypi/photon_core/>`_


Installation
------------

Photon is available as package on pypi, it is called ``photon_core`` [#photon_core]_.

You can install/update the package via pip3 [#pip3]_:

.. code-block:: sh

    pip3 install photon_core

.. code-block:: sh

    pip3 install -U photon_core

.. topic:: Bleeding-Edge

    Development is still at an very early stage, expect anything to change completely in near future.

    As long we still have a leading zero in the version (see *info* file) use *pip3* with the ``--pre`` switch:

    .. code-block:: sh

        pip3 install -U photon_core --pre

.. topic:: Versions

    Tags in the git repository will be released as a new pypi package version.
    Versions of a pypi package has always it's git tag.
    And vice versa.

    Not every version increase will be tagged/released. I will only do so if I feel the urge to do so.

.. [#contributions] Teach me how to write good code, help me to improve.
.. [#photon_core] because photon itself was already taken :/
.. [#pip3] Photon is written in python3 ~ be careful with easy_install