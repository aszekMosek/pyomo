#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

#
# Test the path solver
#

import sys
import importlib
import os
from os.path import abspath, dirname, normpath, join
currdir = dirname(abspath(__file__))
exdir = normpath(join(currdir,'..','..','..','examples','mpec'))

import pyutilib.th as unittest

import pyomo.opt
import pyomo.scripting.pyomo_main as pyomo_main
from pyomo.scripting.util import cleanup
from pyomo.environ import *

from six import iteritems

try:
    import yaml
    yaml_available=True
except ImportError:
    yaml_available=False

solver = pyomo.opt.load_solvers('path')

class CommonTests:

    solve = True
    solver='path'

    def run_solver(self, *_args, **kwds):
        if self.solve:
            args = ['solve']
            args.append('--solver='+self.solver)
            args.append('--save-results=result.yml')
            args.append('--results-format=yaml')
            args.append('--solver-options="lemke_start=automatic output_options=yes"')
        else:
            args = ['convert']
        args.append('-c')
        args.append('--symbolic-solver-labels')
        args.append('--file-determinism=2')

        if False:
            args.append('--stream-solver')
            args.append('--tempdir='+currdir)
            args.append('--keepfiles')
            args.append('--logging=debug')

        args = args + list(_args)
        os.chdir(currdir)

        print('***')
        print(' '.join(args))
        try:
            output = pyomo_main.main(args)
        except SystemExit:
            output = None
        except:
            output = None
            raise
        cleanup()
        print('***')
        return output

    def referenceFile(self, problem, solver):
        return join(currdir, problem+'.txt')

    def getObjective(self, fname):
        FILE = open(fname,'r')
        data = yaml.load(FILE)
        FILE.close()
        solutions = data.get('Solution', [])
        ans = []
        for x in solutions:
            ans.append(x.get('Objective', {}))
        return ans

    def updateDocStrings(self):
        for key in dir(self):
            if key.startswith('test'):
                getattr(self,key).__doc__ = " (%s)" % getattr(self,key).__name__

    def test_munson1a(self):
        self.problem='test_munson1a'
        self.run_solver( join(exdir,'munson1a.py') )
        self.check( 'munson1a', self.solver )

    def test_munson1b(self):
        self.problem='test_munson1b'
        self.run_solver( join(exdir,'munson1b.py') )
        self.check( 'munson1b', self.solver )

    def test_munson1c(self):
        self.problem='test_munson1c'
        self.run_solver( join(exdir,'munson1c.py') )
        self.check( 'munson1c', self.solver )

    def test_munson1d(self):
        self.problem='test_munson1d'
        self.run_solver( join(exdir,'munson1d.py') )
        self.check( 'munson1d', self.solver )

    def check(self, problem, solver):
        refObj = self.getObjective(self.referenceFile(problem,solver))
        ansObj = self.getObjective(join(currdir,'result.yml'))
        self.assertEqual(len(refObj), len(ansObj))
        for i in range(len(refObj)):
            self.assertEqual(len(refObj[i]), len(ansObj[i]))
            for key,val in iteritems(refObj[i]):
                self.assertAlmostEqual(val['Value'], ansObj[i].get(key,None)['Value'], places=2)


@unittest.skipIf(not yaml_available, "YAML is not available")
@unittest.skipIf(solver['path'] is None, "The 'path' executable is not available")
class Solve_PATH(unittest.TestCase, CommonTests):

    def run_solver(self,  *args, **kwds):
        CommonTests.run_solver(self, *args, **kwds)


if __name__ == "__main__":
    unittest.main()
