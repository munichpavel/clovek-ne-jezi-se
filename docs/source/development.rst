Development
===========

First create and enter a virtual environment a la `virtualenvwrapper`_, `conda`_ or your own favorite (if you use `venv`_, you will first have to clone and :code:`cd` into the repository as below so that your virtual environment files are in the right place).

.. code-block:: bash

  git clone https://github.com/munichpavel/clovek-ne-jezi-se
  cd clovek-ne-jezi-se
  pip install -r requirements.txt -r requirements-dev.txt -r requirements-docs.txt


Static code analysis
--------------------

We provide config files and `requirements-dev.txt` dependencies for

* pytest_
* flake8_
* radon_
* coverage_

Please refer to the respective docs for usage help.

Continuous Integration
----------------------

We use `GitHub Actions`_ to run checks. See ``.github/workflows/ci.yaml``.

Pre-commit hooks
----------------

`pre-commit`_ hooks are defined in ``.pre-commit-config.yaml``

.. URLS

.. _`venv`: https://docs.python.org/3/library/venv.html
.. _`virtualenvwrapper`: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _`conda`: https://docs.conda.io/en/latest/
.. _pre-commit: https://pre-commit.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _radon: https://radon.readthedocs.io/en/latest/
.. _coverage: https://coverage.readthedocs.io/en/coverage-5.4/
.. _GitHub Actions: https://docs.github.com/en/actions