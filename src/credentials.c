/*
 * Copyright 2010-2014 The pygit2 contributors
 *
 * This file is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License, version 2,
 * as published by the Free Software Foundation.
 *
 * In addition to the permissions in the GNU General Public License,
 * the authors give you unlimited permission to link the compiled
 * version of this file into combinations with other programs,
 * and to distribute those combinations without any restriction
 * coming from the use of this file.  (The General Public License
 * restrictions do apply in other respects; for example, they cover
 * modification of the file, and distribution when not linked into
 * a combined executable.)
 *
 * This file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; see the file COPYING.  If not, write to
 * the Free Software Foundation, 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301, USA.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include "error.h"
#include "types.h"
#include "utils.h"
#include "oid.h"
#include "refspec.h"
#include "remote.h"

int
CredUsernamePassword_init(CredUsernamePassword *self, PyObject *args, PyObject *kwds)
{
    char *username, *password;

    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError, "CredUsernamePassword takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "ss", &username, &password))
        return -1;

    self->parent.credtype = GIT_CREDTYPE_USERPASS_PLAINTEXT;

    self->username = strdup(username);
    if (!self->username) {
        PyErr_NoMemory();
        return -1;
    }

    self->password = strdup(password);
    if (!self->password) {
        free(self->username);
        PyErr_NoMemory();
        return -1;
    }

    return 0;
}

void
CredUsernamePassword_dealloc(CredUsernamePassword *self)
{
    free(self->username);
    free(self->password);

    PyObject_Del(self);
}

PyMemberDef CredUsernamePassword_members[] = {
    MEMBER(CredUsernamePassword, username, T_STRING, "username"),
    MEMBER(CredUsernamePassword, password, T_STRING, "password"),
    {NULL},
};

PyDoc_STRVAR(CredUsernamePassword__doc__,
  "Credential type for username/password combination");

PyTypeObject CredUsernamePasswordType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.CredUsernamePassword",            /* tp_name           */
    sizeof(CredUsernamePassword),              /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)CredUsernamePassword_dealloc,  /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    0,                                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    CredUsernamePassword__doc__,               /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    CredUsernamePassword_members,              /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)CredUsernamePassword_init,       /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

int
CredSshKey_init(CredSshKey *self, PyObject *args, PyObject *kwds)
{
    char *username, *pubkey, *privkey, *passphrase;

    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError, "CredSshKey takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "ssss", &username, &pubkey,
                                        &privkey, &passphrase))
        return -1;

    self->parent.credtype = GIT_CREDTYPE_SSH_KEY;
    self->username = self->pubkey = self->privkey = self->passphrase = NULL;

    self->username = strdup(username);
    self->pubkey = strdup(pubkey);
    self->privkey = strdup(privkey);
    self->passphrase = strdup(passphrase);

    if (!(self->username && self->pubkey && self->privkey && self->passphrase))
        goto on_oom;

    return 0;

  on_oom:
    free(self->username);
    free(self->pubkey);
    free(self->privkey);
    free(self->passphrase);
    PyErr_NoMemory();
    return -1;
}

void
CredSshKey_dealloc(CredSshKey *self)
{
    free(self->username);
    free(self->pubkey);
    free(self->privkey);
    free(self->passphrase);

    PyObject_Del(self);
}

PyMemberDef CredSshKey_members[] = {
    MEMBER(CredSshKey, username, T_STRING, "username"),
    MEMBER(CredSshKey, pubkey, T_STRING, "pubkey"),
    MEMBER(CredSshKey, privkey, T_STRING, "privkey"),
    MEMBER(CredSshKey, passphrase, T_STRING, "passphrase"),
    {NULL},
};

PyDoc_STRVAR(CredSshKey__doc__,
  "Credential type for an SSH keypair");

PyTypeObject CredSshKeyType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.CredSshKey",                      /* tp_name           */
    sizeof(CredSshKey),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)CredSshKey_dealloc,            /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    0,                                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    CredSshKey__doc__,                         /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    CredSshKey_members,                        /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)CredSshKey_init,                 /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
