#include <pygit2/error.h>

PyObject *GitError;

PyObject * Error_type(int type)
{
    const git_error* error;
    // Expected
    switch (type) {
        /** Input does not exist in the scope searched. */
        case GIT_ENOTFOUND:
            return PyExc_KeyError;

        /** A reference with this name already exists */
        case GIT_EEXISTS:
            return PyExc_ValueError;

        /** The given short oid is ambiguous */
        case GIT_EAMBIGUOUS:
            return PyExc_ValueError;

        /** The buffer is too short to satisfy the request */
        case GIT_EBUFS:
            return PyExc_ValueError;

        /** Skip and passthrough the given ODB backend */
        case GIT_PASSTHROUGH:
            return GitError;

        /** No entries left in ref walker */
        case GIT_REVWALKOVER:
            return PyExc_StopIteration;
    }

    // Critical
    error = giterr_last();
    if(error != NULL) {
        switch (error->klass) {
            case GITERR_NOMEMORY:
                return PyExc_MemoryError;
            case GITERR_OS:
                return PyExc_OSError;
            case GITERR_INVALID:
                return PyExc_ValueError;
        }
    }
    return GitError;
}


PyObject* Error_set(int err)
{
    assert(err < 0);

    if(err != GIT_ERROR) { //expected failure
        PyErr_SetNone(Error_type(err));
    } else { //critical failure
        const git_error* error = giterr_last();
        char* message = (error == NULL) ? 
                "(No error information given)" : error->message;
        
        PyErr_SetString(Error_type(err), message);
    }

    return NULL;
}

PyObject* Error_set_str(int err, const char *str)
{
    const git_error* error;
    if (err == GIT_ENOTFOUND) {
        /* KeyError expects the arg to be the missing key. */
        PyErr_SetString(PyExc_KeyError, str);
        return NULL;
    }

    error = giterr_last();
    return PyErr_Format(Error_type(err), "%s: %s", str, error->message);
}

PyObject* Error_set_oid(int err, const git_oid *oid, size_t len)
{
    char hex[GIT_OID_HEXSZ + 1];

    git_oid_fmt(hex, oid);
    hex[len] = '\0';
    return Error_set_str(err, hex);
}
