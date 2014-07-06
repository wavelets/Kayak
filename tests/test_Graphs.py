import sys
import numpy        as np
import numpy.random as npr

import kayak

from . import *

def test_graph_chain():
    npr.seed(1)

    N  = 10
    D  = 5
    H1 = 6
    H2 = 7

    X  = kayak.Inputs(npr.randn(N,D))
    W1 = kayak.Parameter(npr.randn(D,H1))
    W2 = kayak.Parameter(npr.randn(H1,H2))
    W3 = kayak.Parameter(npr.randn(H2,1))

    U1 = kayak.SoftReLU(kayak.MatMult(X, W1))
    U2 = kayak.SoftReLU(kayak.MatMult(U1, W2))
    U3 = kayak.SoftReLU(kayak.MatMult(U2, W3))
    
    out = kayak.MatSum(U3)

    out.value(True)
    assert kayak.util.checkgrad(W1, out) < MAX_GRAD_DIFF
    assert kayak.util.checkgrad(W2, out) < MAX_GRAD_DIFF
    assert kayak.util.checkgrad(W3, out) < MAX_GRAD_DIFF

def test_graph_diamond():
    npr.seed(2)

    N  = 10
    D  = 5
    H1 = 6
    H2 = 7

    X   = kayak.Inputs(npr.randn(N,D))
    W1  = kayak.Parameter(npr.randn(D,H1))
    W2a = kayak.Parameter(npr.randn(H1,H2))
    W2b = kayak.Parameter(npr.randn(H1,H2))
    W3  = kayak.Parameter(npr.randn(H2,1))

    U1 = kayak.SoftReLU(kayak.MatMult(X, W1))
    U2a = kayak.SoftReLU(kayak.MatMult(U1, W2a))
    U2b = kayak.SoftReLU(kayak.MatMult(U1, W2b))
    U3a = kayak.SoftReLU(kayak.MatMult(U2a, W3))
    U3b = kayak.SoftReLU(kayak.MatMult(U2b, W3))
    
    out = kayak.MatSum(kayak.MatAdd(U3a, U3b))

    out.value(True)
    assert kayak.util.checkgrad(W1, out) < MAX_GRAD_DIFF
    assert kayak.util.checkgrad(W2a, out) < MAX_GRAD_DIFF
    assert kayak.util.checkgrad(W2b, out) < MAX_GRAD_DIFF
    assert kayak.util.checkgrad(W3, out) < MAX_GRAD_DIFF

def test_graph_dag():
    npr.seed(3)

    num_layers = 7
    num_dims   = 5
    
    for ii in xrange(NUM_TRIALS):
        probs = npr.rand()

        X = kayak.Inputs(npr.randn(25,num_dims))

        wts    = []
        layers = []
        for jj in xrange(num_layers):

            U = kayak.Constant(np.zeros((25,num_dims)))

            if npr.rand() < probs:
                W = kayak.Parameter(0.1*npr.randn(num_dims, num_dims))
                wts.append(W)
                U = kayak.MatAdd( U, kayak.SoftReLU(kayak.MatMult(X, W)) )

            for kk in xrange(jj):
                if npr.rand() < probs:
                    W = kayak.Parameter(0.1*npr.randn(num_dims, num_dims))
                    wts.append(W)
                    U = kayak.MatAdd( U, kayak.SoftReLU(kayak.MatMult(layers[kk], W)) )
            
            layers.append(U)
            
        out = kayak.MatSum(layers[-1])

        out.value(True)
        for jj, wt in enumerate(wts):
            diff = kayak.util.checkgrad(wt, out, 1e-4)
            print diff
            assert diff < 1e-4
        

    
