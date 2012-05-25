#include <Python.h>
#include <git2.h>
#include <pygit2/utils.h>
#include <pygit2/error.h>
#include <pygit2/oid.h>

int
py_str_to_git_oid(PyObject *py_str, git_oid *oid)
{
    PyObject *py_hex;
    char *hex_or_bin;
    int err;
    Py_ssize_t len;

    /* Case 1: raw sha */
    if (PyString_Check(py_str)) {
        hex_or_bin = PyString_AsString(py_str);
        if (hex_or_bin == NULL)
            return -1;
        git_oid_fromraw(oid, (const unsigned char*)hex_or_bin);
        return GIT_OID_HEXSZ;
    }

    /* Case 2: hex sha */
    if (PyUnicode_Check(py_str)) {
        py_hex = PyUnicode_AsASCIIString(py_str);
        if (py_hex == NULL)
            return -1;
        err = PyString_AsStringAndSize(py_hex, &hex_or_bin, &len);
        if (err) {
            Py_DECREF(py_hex);
            return -1;
        }

        err = git_oid_fromstrn(oid, hex_or_bin, len);

        Py_DECREF(py_hex);

        if (err < 0) {
            PyErr_SetObject(Error_type(err), py_str);
            return -1;
        }
        return len;
    }

    /* Type error */
    PyErr_Format(PyExc_TypeError,
                 "Git object id must be byte or a text string, not: %.200s",
                 Py_TYPE(py_str)->tp_name);
    return -1;
}

int
py_str_to_git_oid_expand(git_repository *repo, PyObject *py_str, git_oid *oid)
{
    int err;
    int len;
    git_odb *odb;
    git_odb_object *obj;

    len = py_str_to_git_oid(py_str, oid);

    if (len == GIT_OID_HEXSZ || len < 0)
        return len;

    err = git_repository_odb(&odb, repo);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    err = git_odb_read_prefix(&obj, odb, oid, len);
    if (err < 0) {
        git_odb_free(odb);
        Error_set(err);
        return err;
    }

    git_oid_cpy(oid, git_odb_object_id(obj));

    git_odb_object_free(obj);
    git_odb_free(odb);

    return 0;
}

PyObject *
git_oid_to_py_str(const git_oid *oid)
{
    char hex[GIT_OID_HEXSZ];

    git_oid_fmt(hex, oid);
    return PyUnicode_DecodeASCII(hex, GIT_OID_HEXSZ, "strict");
}

