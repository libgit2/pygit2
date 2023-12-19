**********************************************************************
Filters
**********************************************************************

pygit2 supports defining and registering libgit2 blob filters implemented
in Python.

The Filter type
===============

.. autoclass:: pygit2.Filter
   :members:

.. autoclass:: pygit2.FilterSource

Registering filters
===================

.. autofunction:: pygit2.filter_register
.. autofunction:: pygit2.filter_unregister

Example
=======

The following example is a simple Python implementation of a filter which
enforces that blobs are stored with unix LF line-endings in the ODB, and
checked out with line-endings in accordance with the .gitattributes ``eol``
setting.

.. code-block:: python

    class CRLFFilter(pygit2.Filter):
        attributes = "text eol=*"

        def __init__(self):
            super().__init__()
            self.linesep = b'\r\n' if os.name == 'nt' else b'\n'
            self.buffer = io.BytesIO()

        def check(self, src, attr_values):
            if src.mode == GIT_FILTER_SMUDGE:
                # attr_values contains the values of the 'text' and 'eol'
                # attributes in that order (as they are defined in
                # CRLFFilter.attributes
                eol = attr_values[1]

                if eol == 'crlf':
                    self.linesep = b'\r\n'
                elif eol == 'lf':
                    self.linesep = b'\n'
            else:  # src.mode == GIT_FILTER_CLEAN
                # always use LF line-endings when writing to the ODB
                self.linesep = b'\n'

        def write(data, src, write_next):
            # buffer input data in case line-ending sequences span chunk boundaries
            self.buffer.write(data)

        def close(self, write_next):
            # apply line-ending conversion to our buffered input and write all
            # of our output data
            self.buffer.seek(0)
            write_next(self.linesep.join(self.buffer.read().splitlines()))
