#!/usr/bin/env python3

from qatrfm.testcase import TrfmTestCase
from qatrfm.utils.logger import QaTrfmLogger

logger = QaTrfmLogger.getQatrfmLogger(__name__)

""" Custom test example
"""


class CustomTest(TrfmTestCase):

    def __init__(self, env, name):
        description = "Example using a custom .tf file"
        super(CustomTest, self).__init__(env, name, description)

    def run(self):
        self.logger.info('Running test case {}'.format(self.name))
        vm1 = self.env.domains[0]
        vm1.execute_cmd('ip address show')
        vm1.execute_cmd('cat /etc/os-release')
        return self.EX_OK
