# -*- codint:utf-8 -*-

import os
import filecmp
import subprocess

import unittest
from unittest import TestCase
from RMC.controller.rmc import RMCController


class TestRMCController(TestCase):
    controller = None
    base_dir = None
    all_original_file = None

    @classmethod
    def setUp(cls):
        inp = 'resources/RMCController/inp'
        cls.base_dir = os.path.dirname(inp)
        archive = os.path.join(cls.base_dir, 'archive')
        cls.controller = RMCController(inp, archive)
        cls.all_original_file = os.listdir(cls.base_dir)

    @classmethod
    def tearDown(cls):
        all_file = os.listdir(cls.base_dir)
        all_new_file = list(set(all_file) - set(cls.all_original_file))
        for file in all_new_file:
            os.remove(os.path.join(cls.base_dir, file))

    def test_check(self):
        inp = 'resources/inp'
        status_file = 'resources/status.txt'
        controller = RMCController(inp)
        result = controller.check(status_file)
        self.assertEqual(result, [True])

    def test_new_inp_archive(self):
        self.assertEqual(self.controller.new_inp_archive(),
                         ['resources/RMCController/inp.burnup.0.couple.1',
                          'resources/RMCController/archive/burnup0/couple1'])

    def test_generate_tally_hdf(self):
        self.controller.generate_tally_hdf(
            self.controller.model['tally'].meshtally[0], self.base_dir)
        h5diff = 'h5diff -r --delta=1E-15 ' + \
                 os.path.join(self.base_dir, 'reference.h5') + ' ' +\
                 os.path.join(self.base_dir, 'MeshTally1.h5')
        p_h5diff = subprocess.Popen(h5diff, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True,
                                    universal_newlines=True)
        p_h5diff_out, p_h5diff_err = p_h5diff.communicate()
        returncode = p_h5diff.poll()
        try:
            self.assertEqual(returncode, 0)
        except AssertionError:
            print("h5diff command has detected the following differences:")
            print(p_h5diff_out)
            print("h5diff command has detected the following errors:")
            print(p_h5diff_err)
            exit(returncode)

    def test_continuing(self):
        controller_property = {'inp': 'inp', 'archive': 'archive'}

        # 设置条件
        self.controller.last_archive = \
            os.path.join(self.base_dir, 'archive', 'burnup1', 'couple6')
        self.controller.last_inp = \
            os.path.join('inp.burnup.1.couple.6')
        self.controller.iteration = 3
        self.controller.model['burnup'].current_step = 2

        # 测试函数生成的文件
        self.controller.continuing('resources/status.txt', controller_property)
        self.assertTrue(
            filecmp.cmp(controller_property['inp'],
                        os.path.join(self.base_dir, 'reference_inp')),
            'new input file generated by func:continuing is not matched!'
        )


if __name__ == '__main__':
    unittest.main()
