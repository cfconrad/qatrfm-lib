#!/usr/bin/env python

import time
import sys

from qatrfm.environment import TerraformEnv
from qatrfm.testcase import TrfmTestCase


class MyTestCase(TrfmTestCase):
    def run(self):
        # test logic here
        self.logger.info('Running test case {}'.format(self.name))
        vm1 = self.env.domains[0]
        # Stop firewall to allow SSH transfers
        # It could be also disabled by default in the image
        # [retcode, output] = vm1.execute_cmd('systemctl stop firewalld')
        # time.sleep(20)
        vm1.transfer_file(remote_file_path='/etc/resolv.conf',
                          local_file_path='/root/test.resolv.conf',
                          type='get')


def main():
    env = TerraformEnv(num_domains=1)
    env.deploy()
    exit_status = TrfmTestCase.EX_OK

    try:
        test = MyTestCase(env, 'simple_test', 'Create a VM and transfer files')
        if (test.run() != TrfmTestCase.EX_OK):
            exit_status = TrfmTestCase.EX_RUN_ERROR

    except Exception as e:
        print("Something went wrong:\n{}".format(e))
        env.clean()
        sys.exit(TrfmTestCase.EX_RUN_ERROR)

    env.clean()
    print("The test finished with status={}".format(exit_status))
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
