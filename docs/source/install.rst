============
Installation
============

SuperDetectorPy is a command-line Python program that depends on Numpy, Scipy, Matplotlib, and h5py. Using a Python environment like Anaconda is recommended, since it guarantees that the correct versions are installed. Mesh generation is done in Matlab using the PDE toolbox.

This guide provides help with installing SuperDetectorPy and all its dependencies. The instructions have been tested on Ubuntu 20.04, Ubuntu 22.04, and Windows 10.

Required programs
=================

SuperDetectorPy requires the following programs to be installed on your computer.

- Matlab with the `PDE toolbox <https://se.mathworks.com/products/pde.html>`_.

- `Anaconda <https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html>`_ (recommended), `Miniconda <https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html>`_, or `virtualenv <https://virtualenv.pypa.io/en/latest/installation.html>`_.

- ffmpeg (optional, only used for generating animations).

Download SuperDetectorPy
========================

Go to SuperDetectorPy's `release page <https://github.com/afsa/super-detector-py/releases>`_, download the latest version (``Source code (zip)``), and unzip the file.

Alternatively, in a Linux terminal run

.. code-block:: bash

    wget -O super-detector-py.zip https://github.com/afsa/super-detector-py/archive/refs/tags/v1.0.1.zip && \
    unzip super-detector-py.zip && \
    rm super-detector-py.zip

Setup a Python environment
==========================

It is recommended to setup a Python environment for SuperDetectorPy to guarantee that the correct versions of packages are used. The Python environment Anaconda is recommended for SuperDetectorPy, but virtualenv also works.

Using Anaconda / Miniconda (recommended)
----------------------------------------

Open a terminal with ``conda`` available (called Anaconda Prompt on Windows) and navigate to the root of the SuperDetectorPy repository. Run the following commands to setup the environment and install dependencies:

.. code-block:: bash

    conda create -yn SuperDetectorPy python=3.8
    conda install -n SuperDetectorPy pip
    conda activate SuperDetectorPy
    pip install -r requirements.txt

Verify that the installation was successful by running:

.. code-block:: bash

    python simulate.py -h

.. note::

    The ``SuperDetectorPy`` Anaconda environment needs to be active when running Python scripts in this repository. If the environment has been deactivated, then run the following command in terminal with ``conda`` available:

    .. code-block:: bash

        conda activate SuperDetectorPy

Using virtualenv
----------------

SuperDetectorPy only works with ``python3`` and has only been tested using virtualenv with ``python3.8`` on Ubuntu 20.04. If multiple Python versions are installed, then virtualenv's ``--python`` option may be used to specify the version.

Open a terminal, navigate to the root of the SuperDetectorPy repository, and run:

.. code-block:: bash

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

Verify that the installation was successful by running:

.. code-block:: bash

    python simulate.py -h

.. note::

    The virtual environment needs to be active when running Python scripts in this repository. If the environment has been deactivated, then run the following command in the root of the repository:

    .. code-block:: bash

        source venv/bin/activate