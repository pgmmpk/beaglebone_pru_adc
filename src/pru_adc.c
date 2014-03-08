/*
 * beaglebone_pru_adc - fast analog sensor capture for BeagleBone Black
 *
 * @author Mike Kroutikov
 * @email: pgmmpk@gmail.com
 */

#include <Python.h>
#include <stddef.h>

#include "prussdrv.h"
#include "pruss_intc_mapping.h"
#include "firmware.h"

typedef struct {
	PyObject_HEAD
	
	locals_t locals;
	
	int started;
	int closed;
	
} Capture;

static void Capture_dealloc(Capture	 *self) {
	if (!self->closed) {
		self->closed = 1;
		
		prussdrv_exit();
	}
	
	Py_TYPE(self)->tp_free((PyObject*)self);
}

static int Capture_init(Capture *self, PyObject *args, PyObject *kwds) {
	tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_INITDATA;
	int rc;
	
	self->closed = 1; // consider closed unless successfully init everything
	
	rc = prussdrv_init ();
	if (rc != 0) {
		PyErr_SetString(PyExc_IOError, "Failed to init PRUSSDRV driver");
		return -1;
	}
	
	rc = prussdrv_open(0);
	if (rc != 0) {
		PyErr_SetString(PyExc_IOError, "Failed to open PRU 0");
		prussdrv_exit();
		return -1;
	}
	
	rc = prussdrv_pruintc_init(&pruss_intc_initdata);		// Get the interrupt initialized
	if (rc != 0) {
		PyErr_SetString(PyExc_IOError, "Failed to initialize interrupts");
		prussdrv_exit();
		return -1;
	}

	memset(&self->locals, 0, sizeof(self->locals));
	self->locals.eyecatcher = EYECATCHER;
	self->locals.enc.encoder0 = 0xff; // assigning out-of-range pin number disables encoder logic
	self->locals.enc.encoder1 = 0xff; // ditto
	
	self->locals.enc_local[0].threshold = 2000;
	self->locals.enc_local[0].speed = INITIAL_ACC_VAL;
	self->locals.enc_local[0].acc = INITIAL_ACC_VAL;
	
	self->locals.enc_local[1].threshold = 2000;
	self->locals.enc_local[1].speed = INITIAL_ACC_VAL;
	self->locals.enc_local[1].acc = INITIAL_ACC_VAL;
	
	rc = prussdrv_pru_write_memory(0, 0, (unsigned int *) &self->locals, sizeof(self->locals));
	if (rc < 0) {
		PyErr_SetString(PyExc_IOError, "Failed to write local memory block");
		prussdrv_exit();
		return -1;
	}

	self->closed = 0;
	
	return 0;
}

static PyObject *Capture_start(Capture *self, PyObject *args, PyObject *kwds) {
	int rc;
	char *filename = NULL;
	
	if (!PyArg_ParseTuple(args, "s", &filename)) {		// Parse the PRU number
		return NULL;
	}
	
	if (self->started) {
		PyErr_SetString(PyExc_IOError, "Already started");
		return NULL;
	}
	
	rc = prussdrv_exec_program (0, filename);						// Load and execute the program
	if (rc != 0) {
		PyErr_SetString(PyExc_IOError, "Failed to exec firmware");
		return NULL;
	}
	
	self->started = 1; // true
	
	Py_RETURN_NONE;
}

static PyObject *Capture_wait(Capture *self) {
	
	if (!self->started) {
		PyErr_SetString(PyExc_IOError, "Not started");
		return NULL;
	}
	
	prussdrv_pru_wait_event(0);		// Wait for the event. This blocks the thread.
	prussdrv_pru_clear_event(0, 0);	// Clear the event. FIXME: parameter meaning???
	
	Py_RETURN_NONE;
}

static PyObject *Capture_close(Capture *self, PyObject *args, PyObject *kwds) {
	if (!self->closed) {
		self->closed = 1; // true
		
		prussdrv_exit();
	}
	
	Py_RETURN_NONE;
}

static PyMethodDef Capture_methods[] = {
	{"start", (PyCFunction) Capture_start, METH_VARARGS, "Starts capturing ADC data"},
	{"wait", (PyCFunction) Capture_wait, METH_NOARGS, "Waits for PRU0 interrupt"},
	{"close", (PyCFunction) Capture_close, METH_NOARGS, "closes Capture object"},
	{NULL}  /* Sentinel */
};

static PyTypeObject CaptureType = {
	PyObject_HEAD_INIT(NULL)
	0,						 /*ob_size*/
	"_pru_adc.Capture",		/*tp_name*/
	sizeof(Capture),		   /*tp_basicsize*/
	0,						 /*tp_itemsize*/
	(destructor)Capture_dealloc,		  /*tp_dealloc*/
	0,						 /*tp_print*/
	0,						 /*tp_getattr*/
	0,						 /*tp_setattr*/
	0,						 /*tp_compare*/
	0,						 /*tp_repr*/
	0,						 /*tp_as_number*/
	0,						 /*tp_as_sequence*/
	0,						 /*tp_as_mapping*/
	0,						 /*tp_hash */
	0,						 /*tp_call*/
	0,						 /*tp_str*/
	0,						 /*tp_getattro*/
	0,						 /*tp_setattro*/
	0,						 /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"fast ADC capture object",				 /* tp_doc */
	0,					   /* tp_traverse */
	0,					   /* tp_clear */
	0,					   /* tp_richcompare */
	0,					   /* tp_weaklistoffset */
	0,					   /* tp_iter */
	0,					   /* tp_iternext */
	Capture_methods,	   /* tp_methods */
	0,						 /* tp_members */
	0,						 /* tp_getset */
	0,						 /* tp_base */
	0,						 /* tp_dict */
	0,						 /* tp_descr_get */
	0,						 /* tp_descr_set */
	0,						 /* tp_dictoffset */
	(initproc) Capture_init,   /* tp_init */
	0,						 /* tp_alloc */
	0,						 /* tp_new */
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
