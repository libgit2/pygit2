#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <pygit2/error.h>
#include <pygit2/types.h>
#include <pygit2/utils.h>
#include <pygit2/diff.h>

extern PyTypeObject DiffType;
extern PyTypeObject HunkType;

static int diff_data_cb(
  void *cb_data,
  git_diff_delta *delta,
  git_diff_range *range,
  char usage,
  const char *line,
  size_t line_len)
{
    PyObject *hunks, *tmp;
    Hunk *hunk;
    Py_ssize_t size; 

    hunks = PyDict_GetItemString(cb_data, "hunks");
    if(hunks == NULL)
      return -1;

    size = PyList_Size(hunks);
    hunk = (Hunk*) PyList_GetItem(hunks, size-1);
    if(hunk == NULL)
      return -1;

    tmp = PyBytes_FromStringAndSize(line, line_len);

    if(usage != GIT_DIFF_LINE_DELETION)
        PyBytes_Concat(&hunk->new_data, tmp);

    if(usage != GIT_DIFF_LINE_ADDITION)
        PyBytes_Concat(&hunk->old_data, tmp);

  return 0;
}

static int diff_hunk_cb(
  void *cb_data,
  git_diff_delta *delta,
  git_diff_range *range,
  const char *header,
  size_t header_len)
{
  PyObject *hunks;
  Hunk *hunk;

  hunks = PyDict_GetItemString(cb_data, "hunks");
  if(hunks == NULL) {
    hunks = PyList_New(0);
    PyDict_SetItemString(cb_data, "hunks", hunks);
  }

  hunk = (Hunk*) PyType_GenericNew(&HunkType, NULL, NULL);

  hunk->old_start = range->old_start;
  hunk->old_lines = range->old_lines;
  hunk->new_start = range->new_start;
  hunk->new_lines = range->new_lines;

  int len;
  char* old_path, *new_path;

  len = strlen(delta->old_file.path) + 1;
  old_path = malloc(sizeof(char) * len);
  memcpy(old_path, delta->old_file.path, len);
  hunk->old_file = old_path;

  len = strlen(delta->new_file.path) + 1;
  new_path = malloc(sizeof(char) * len);
  memcpy(new_path, delta->new_file.path, len);
  hunk->new_file = new_path;

#if PY_MAJOR_VERSION >= 3
  hunk->old_data = Py_BuildValue("y", "");
  hunk->new_data = Py_BuildValue("y", "");
#else
  hunk->old_data = Py_BuildValue("s", "");
  hunk->new_data = Py_BuildValue("s", "");
#endif

  PyList_Append(hunks, (PyObject*) hunk);

  return 0;
};

static int diff_file_cb(void *cb_data, git_diff_delta *delta, float progress)
{
    PyObject *files, *file;

    files = PyDict_GetItemString(cb_data, "files");
    if(files == NULL) {
      files = PyList_New(0);
      PyDict_SetItemString(cb_data, "files", files);
    }

    file = Py_BuildValue("(s,s,i)",
        delta->old_file.path,
        delta->new_file.path,
        delta->status
    );

    PyList_Append(files, file);

    return 0;
}

PyObject *
Diff_changes(Diff *self)
{
    git_diff_options opts = {0};
    git_diff_list *changes;
    int err;

    err = git_diff_tree_to_tree(
              self->t0->repo->repo,
              &opts,
              self->t0->tree,
              self->t1->tree,
              &changes);

    if(err < 0) {
        Error_set(err);
        return NULL;
    }
    
    PyObject *payload;
    payload = PyDict_New();

    git_diff_foreach(
      changes,
      payload,
      &diff_file_cb,
      &diff_hunk_cb,
      &diff_data_cb
    );
    git_diff_list_free(changes);

    return payload;
}

static int diff_print_cb(
  void *cb_data,
  git_diff_delta *delta,
  git_diff_range *range,
  char usage,
  const char *line,
  size_t line_len)
{
  PyObject *data = PyBytes_FromStringAndSize(line, line_len);
  PyBytes_ConcatAndDel((PyObject**) cb_data, data);

  return 0;
}


PyObject *
Diff_patch(Diff *self)
{
    git_diff_options opts = {0};
    git_diff_list *changes;
    int err;

    err = git_diff_tree_to_tree(
              self->t0->repo->repo,
              &opts,
              self->t0->tree,
              self->t1->tree,
              &changes);

    if(err < 0) {
        Error_set(err);
        return NULL;
    }

    PyObject *patch = PyBytes_FromString("");

    git_diff_print_patch(changes, &patch, &diff_print_cb);

    return patch;
}

static int
Hunk_init(Hunk *self, PyObject *args, PyObject *kwds)
{
      self->old_start = 0;
      self->old_lines = 0;

      self->new_start = 0;
      self->new_lines = 0;

      self->old_data = PyString_FromString("");
      if (self->old_data == NULL) {
        Py_DECREF(self);
        return -1;
      }

      self->new_data = PyString_FromString("");
      if (self->new_data == NULL) {
        Py_DECREF(self);
        return -1;
      }

      return 0;
}

static void
Hunk_dealloc(Hunk *self)
{
    Py_XDECREF(self->old_data);
    Py_XDECREF(self->new_data);
    PyObject_Del(self);
}

PyMemberDef Hunk_members[] = {
    {"old_start", T_INT, offsetof(Hunk, old_start), 0, "old start"},
    {"old_lines", T_INT, offsetof(Hunk, old_lines), 0, "old lines"},
    {"old_file",  T_STRING, offsetof(Hunk, old_file), 0, "old file"},
    {"old_data",  T_OBJECT, offsetof(Hunk, old_data), 0, "old data"},
    {"new_start", T_INT, offsetof(Hunk, new_start), 0, "new start"},
    {"new_lines", T_INT, offsetof(Hunk, new_lines), 0, "new lines"},
    {"new_file",  T_STRING, offsetof(Hunk, new_file), 0, "old file"},
    {"new_data",  T_OBJECT, offsetof(Hunk, new_data), 0, "new data"},
    {NULL}
};

PyTypeObject HunkType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Hunk",                             /* tp_name           */
    sizeof(Hunk),                              /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Hunk_dealloc,                  /* tp_dealloc        */
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
    "Hunk object",                             /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    Hunk_members,                              /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Hunk_init,                       /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};


static void
Diff_dealloc(Diff *self)
{
    Py_XDECREF(self->t0);
    Py_XDECREF(self->t1);
    PyObject_Del(self);
}


PyGetSetDef Diff_getseters[] = {
    {"changes", (getter)Diff_changes, NULL, "raw changes", NULL},
    {"patch", (getter)Diff_patch, NULL, "patch", NULL},
    {NULL}
};


PyTypeObject DiffType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Diff",                             /* tp_name           */
    sizeof(Diff),                              /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Diff_dealloc,                  /* tp_dealloc        */
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
    "Diff objects",                            /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Diff_getseters,                            /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
