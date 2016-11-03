# -*- coding: utf-8 -*-
"""
Created on Thu Nov 03 12:53:28 2016

@author: admin
"""

import unittest
import importlib
import imp, os
import sys, inspect
from os import path
import difflib


sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
fileName, pathname, description = imp.find_module('infodens')



prep = imp.load_source('preprocess', pathname+'/preprocessor/preprocess.py')
prepObj = prep.Preprocess('testFile.txt')

from infodens.featurextractor import lexicalFeatures
#surf = imp.load_source('surfaceFeatures', pathname+'/featurextractor/surfaceFeatures.py')
lexObj = lexicalFeatures.LexicalFeatures(prepObj)

class Test_lexicalFeatures(unittest.TestCase):

    def test_lexicalDensity(self):
        c = [0.5, 0.25, 0.5, 0.25]
        ch = lexObj.lexicalDensity('J,N,R,V')
        self.assertListEqual(c,ch)
        
    def test_lexicalRichness(self):
        c = [1.0, 1.0, 1.0, 1.0]
        ch = lexObj.lexicalRichness('argString')
        self.assertListEqual(c,ch)
    
    def test_lexicalToTokens(self):
        c = [0.5, 1.0, 0.5, 1.0]
        ch = lexObj.lexicalToTokens('CC,DT,WDT,IN,PDT')
        self.assertListEqual(c,ch)
        
   
        
    
        
    
        
if __name__ == '__main__':
    unittest.main()