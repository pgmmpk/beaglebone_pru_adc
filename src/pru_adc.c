/*
 * beaglebone_pru_adc - fast analog sensor capture for BeagleBone Black
 *
 * @author Mike Kroutikov
 * @email: pgmmpk@gmail.com
 */

#include <Python.h>
#include "prussdrv.h"

typedef struct {
    PyObject_HEAD
    
    void *pin;

} Capture;

static void Capture_dealloc(Capture	 *self) {
    if (self->pin != NULL)
    {
        self->pin = NULL;
    }

    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int Capture_init(Capture *self, PyObject *args, PyObject *kwds) {
    char *channel;

    self->pin = NULL;

    if (!PyArg_ParseTuple(args, "s", &channel))
        return -1;

    return 0;
}

static PyObject *Capture_start(Capture *self, PyObject *args, PyObject *kwds) {
    float value;
    int success;

    if (self->pin == NULL)
    {
        PyErr_SetString(PyExc_IOError, "Can not read closed AIN pin.");
        return NULL;
    }

    if (success != 0)
    {
        PyErr_SetFromErrnoWithFilename(PyExc_IOError, "Error reading AIN pin.");
        return NULL;
    }

    return Py_BuildValue("f", value);
}

static PyObject *Capture_stop(Capture *self, PyObject *args, PyObject *kwds) {
    float value;
    int success;

    if (self->pin == NULL)
    {
        PyErr_SetString(PyExc_IOError, "Can not read closed AIN pin.");
        return NULL;
    }

    if (success != 0)
    {
        PyErr_SetFromErrnoWithFilename(PyExc_IOError, "Error reading AIN pin.");
        return NULL;
    }

    //scale modifier
    value = value / 1800.0;

    return Py_BuildValue("f", value);
}

static PyObject *Capture_close(Capture *self, PyObject *args, PyObject *kwds) {
    
    if (self->pin != NULL) {
        self->pin = NULL;
    }

    Py_RETURN_NONE;
}

static PyMethodDef Capture_methods[] = {
    {"start", (PyCFunction) Capture_start, METH_NOARGS, "Starts capturing ADC data"},
    {"stop", (PyCFunction) Capture_stop, METH_NOARGS, "Stops capturing ADC data. Capture object can no longer be used"},
    {"close", (PyCFunction) Capture_close, METH_NOARGS, "closes Capture object"},
    {NULL}  /* Sentinel */
};

static PyTypeObject CaptureType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_pru_adc.Capture",        /*tp_name*/
    sizeof(Capture),           /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Capture_dealloc,          /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "fast ADC capture object",                 /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Capture_methods,       /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc) Capture_init,   /* tp_init */
    0,                         /* tp_alloc */
    0,                         /* tp_new */
};

static PyMethodDef module_methods[] = {
    { NULL, NULL, 0, NULL }
};
 
PyMODINIT_FUNC init_pru_adc() {
    PyObject *module = NULL;


    CaptureType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&CaptureType) < 0)
        return;

    module = Py_InitModule3("_pru_adc", module_methods, "");
    if (module == NULL) {
        return;
    }

    Py_INCREF(&CaptureType);
    PyModule_AddObject(module, "Capture", (PyObject *) &CaptureType);
}
