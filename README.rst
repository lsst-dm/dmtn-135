.. image:: https://img.shields.io/badge/dmtn--135-lsst.io-brightgreen.svg
   :target: https://dmtn-135.lsst.io
.. image:: https://github.com/lsst-dm/dmtn-135/workflows/CI/badge.svg
   :target: https://github.com/lsst-dm/dmtn-135/actions/



####################################################################
DM sizing model and purchase plan for the remainder of construction.
####################################################################

DMTN-135
========

This simplified model is based on real machine architectures we have today. We define the needs for commissioning and separately identify the DR1,2 needs which could be moved to operations. This is presented in s series of tables within this document describing the approach taken.

Links
=====

- Live drafts: https://dmtn-135.lsst.io
- GitHub: https://github.com/lsst-dm/dmtn-135

Build
=====

This repository includes lsst-texmf_ as a Git submodule.
Clone this repository::

    git clone --recurse-submodules https://github.com/lsst-dm/dmtn-135

Compile the PDF::

    make

Clean built files::

    make clean

Tables
------

CI regenerates both sets of tables before building the PDF.

Construction-era tables come from the original Google backing sheet::

    make tables

Operations-update tables (``update2026/tables/``) come from the tags of
`lsst/rubin-sizing-model <https://github.com/lsst/rubin-sizing-model>`_ listed in
``sizing-models.toml``. Needs ``git`` and `uv <https://docs.astral.sh/uv/>`_::

    make sizing-tables          # regenerate from the pinned tags
    make sizing-tables-check    # fail if the committed tables are stale

For one model this is equivalent to::

    git clone --branch v2026.10.0 https://github.com/lsst/rubin-sizing-model
    cd rubin-sizing-model
    uv run generate_model.py --emit-tex ../dmtn-135/update2026/tables

To cite a new model version, tag the sizing-model repository, update ``ref`` in
``sizing-models.toml``, run ``make sizing-tables`` and commit the tables with it.
To add a scenario, add a ``[[model]]`` entry with its own parameter file, output
directory and macro prefix.

Updating acronyms
-----------------

A table of the technote's acronyms and their definitions are maintained in the `acronyms.tex` file, which is committed as part of this repository.
To update the acronyms table in ``acronyms.tex``::

    make acronyms.tex

*Note: this command requires that this repository was cloned as a submodule.*

The acronyms discovery code scans the LaTeX source for probable acronyms.
You can ensure that certain strings aren't treated as acronyms by adding them to the `skipacronyms.txt <./skipacronyms.txt>`_ file.

The lsst-texmf_ repository centrally maintains definitions for LSST acronyms.
You can also add new acronym definitions, or override the definitions of acronyms, by editing the `myacronyms.txt <./myacronyms.txt>`_ file.

Updating lsst-texmf
-------------------

`lsst-texmf`_ includes BibTeX files, the ``lsstdoc`` class file, and acronym definitions, among other essential tooling for LSST's LaTeX documentation projects.
To update to a newer version of `lsst-texmf`_, you can update the submodule in this repository::

   git submodule update --init --recursive

Commit, then push, the updated submodule.

.. _lsst-texmf: https://github.com/lsst/lsst-texmf
