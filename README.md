# QA Terraform Library

This is library to execute tests on virtual machines managed by Terraform + Libvirt provider.

## Table of Content
- [Introduction and Goals](#intro)
- [Quickstart](#quickstart)
    - [Installation](#installation)
    - [Usage](#usage)
- [Writting a test case](#writting-a-test-case)
- [Developer guide](#developer-guide)
    - [Multi test](#multi-test)
    - [Reset environment](#reset-environment)
    - [Troubleshooting a test](#troubleshooting-a-test)
    - [Custom .tf files](#custom-tf-files)
- [Authors](#authors)


# Introduction and Goals

Terraform is a tool to easy manage different service providers (IaaS, PaaS, SaaS) in a common way. The only thing Terraform needs is a configuration file which defines the infrastructure to be deployed, with different resource types and options for each provider but written in a similar way.

For more information, refer to the [Terraform website][trfm1]

There is a list of [supported providers][trfm2] but this library focuses on the [Libvirt provider][trfm3].
Terraform talks to libvirtd to create the needed resources (network, disk, domains) in a very simple way.

This library allows interacting easily with Domains (Virtual Machines) created by Terraform + Libvirt. It provides a simple method to get domain objects and perform some actions on them (i.e. run commands, transfer files via scp, ...).

# QuickStart
### Installation
The library can be installed as a python package:

    git clone https://github.com/jlausuch/qatrfm-lib.git
    cd qatrfm-lib
    pip3 install .

It also installs a command in /usr/bin/qatrfm

    qatrfm --version

which performs the following actions:
1) Create and deploys a Terraform environment given some input parameters (number of domains, cores, ram, etc.)
2) Run the test(s) case(s) using the domains in the environment
3) Clean the Terraform environment

### Usage

The command provides comprehensive help of all the needed parameters.

    $ qatrfm -h
    Usage: qatrfm [OPTIONS]

      Create a terraform environment and run the test(s)

    Options:
      -v, --version
      -t, --test TEXT            Testcase(s) name(s). Single name or a list
                                 separated by comas of the Class(es) in path to be
                                 executed.  [required]
      -p, --path TEXT            Path of the test file.  [required]
      -d, --hdd TEXT             Path to HDD image.  [required]
      -n, --num_domains INTEGER  Number of domains to be created. Default=1
      -c, --cores INTEGER        Num cores of the domains. Default=1
      -r, --ram INTEGER          Ram of the domains in MB. Default=1024
      -s, --snapshots            Create snapshots of the domains at the beginning.
                                 This is useful to allow the test revert the
                                 domains to their initial state if needed.
      --no-clean                 Don't clean the environment when the tests
                                 finish. This is useful for debug and
                                 troubleshooting.
      -h, --help                 Show this message and exit.

Some of these parameters are required and some others can be left out if the default values are ok for the user.

If the environment variable LOG_COLORS=1 is set in the system, the command will output logging information using color codes for each message type. This is useful for manual usage of it. Colors are disabled by default.

***IMPORTANT***:
It is recommended to use this tool as root user, since it requires special privileges to create the resources on the system.

### Writing a test case

Although there is a test directory with some examples, let's explain how to write a test case from scratch.

Create a directory within `tests/` and a file with .py extension within.
For instance

    mkdir ./tests/mytest
    touch ./tests/mytest/my_first_test.py

In this python file, a Class inherited from `TrfmTestCase` shall be created for each test case.
This example shows a simple test case which executes a dummy command on a domain.

    #!/usr/bin/env python3
    from qatrfm.testcase import TrfmTestCase

    class MyFirstTest(TrfmTestCase):
        def run(self):
            vm = self.env.domains[0]
            [retcode, output] = vm.execute_cmd('hostname')
            return retcode

The method `run()` shall be overriden from the parent class `TrfmTestCase` and place all the test logic flow there.

The Domain objects are stored in the variable `self.env.domains` as an array of size depending on how many domains are created (1 by default).

It is possible to override the `__init__` method to provide a description of the test case.

    class MyFirstTest(TrfmTestCase):
        def __init__(self, env, name):
            description = "Description of my first test"
            super(SimpleTest, self).__init__(env, name, description)
        ...

To run this test case, you can do the following call:

    $ qatrfm -t MyFirstTest \
             -p /path/to/qatrfm-lib/tests/mytest/my_first_test.py \
             -d /var/lib/libvirt/images/my_image.qcow2 \

Here, `-t MyFirstTest` is the name of the Class which is implemented in the python module defined by `-p /path/to/qatrfm-lib/tests/mytest/my_first_test.py`. This is important so that the program can load dynamically the python module and execute the run() method in that class.

The parameter `--hdd` or `-d` is the path to the source image that libvirt will use to create additional disks for the domains. This file won't be modified.

***IMPORTANT***:
The image provided must be *auto-bootable*. This means for instance that `GRUB_TIMEOUT` shall be different than `-1` for Linux systems. Otherwise the program will timeout waiting for the domains to be up.

**NOTE**: By default, terraform will create 1 domain (Virtual Machine) unless specified by parameter `-n/--num_domains` in the `qatrfm` command.



# Developer guide
### Multi test

It is possible to create more than 1 test in the same python module.
This is useful to re-use the same environment and save time deploying a new one.

The previous example would become something like this:

    #!/usr/bin/env python3
    from qatrfm.testcase import TrfmTestCase

    class MyTest1(TrfmTestCase):
        def run(self):
            vm = self.env.domains[0]
            [retcode, output] = vm.execute_cmd('hostname')
            return retcode

    class MyTest2(TrfmTestCase):
        def run(self):
            vm = self.env.domains[0]
            [retcode, output] = vm.execute_cmd('date')
            return retcode

To run both tests in the same environment, both classes names shall be passed to the `qatrfm` command separated by commas.
Example:

    $ qatrfm -t MyTest1,MyTest2 \
             -p /path/to/qatrfm-lib/tests/mytest/my_first_test.py \
             -d /var/lib/libvirt/images/my_image.qcow2 \

This will run `MyTest1` and `MyTest2` consecutively.

### Reset environment
For multi-test approaches, it is important to mention that sometimes it is useful to reset the environment after each test execution, so we have a freshly installed OS before executing the test flow.

By calling `qatrfm` with the flag `--snapshots`, the library will create a libvirt snapshot of each domain right after deployment. During the test flow, it is possible to call this method to revert the domains to their original state:

    self.env.reset()

For the previous example, this would be:

    #!/usr/bin/env python3
    from qatrfm.testcase import TrfmTestCase

    class MyTest1(TrfmTestCase):
        def run(self):
            vm = self.env.domains[0]
            [retcode, output] = vm.execute_cmd('hostname')
            self.env.reset()
            return retcode

    class MyTest2(TrfmTestCase):
        def run(self):
            vm = self.env.domains[0]
            [retcode, output] = vm.execute_cmd('date')
            return retcode

### Troubleshooting a test
This library will clean the environment after test execution or if any error occurred. When developing a test case, it is useful to troubleshoot the test flow connecting to the domains and run commands manually.

To do that, the flag `--no-clean` must be passed to the `qatrfm` command.


***IMPORTANT:***
The user is responsible to clean the environment manually when finished. This can be done by going to the `basename` directory of the environment and run:

    terraform destroy -auto-approve

### Custom .tf files ###

By default, the library provides a base .tf file with some flexibility when it comes to creating the domains.
It is possible to define the number of domains, the source image, the number of Cores and RAM but sometimes the test needs a different configuration (e.g. 2 NICs in the domains, 2 libvirt Networks, etc.). Therefore, it is possible to place a custom .tf file in the same directory as the python module for the test. The library will check that there is a .tf file and will load it instead of the default one.

The custom .tf file must be similar to the one located in `qatrfm/config/simple_1net.tf` when it comes to input and output variables. However, it is possible to hardcode some of them such as Cores, RAM, etc. but it is recommended to leave intact some of them such as `image`, `basename` and `network`.

Also, the output data that defines the domain names is mandatory in this file and must be present:

    output "domain_names" {
        value = "${libvirt_domain.domain-sle.*.name}"
    }
and optionally and recommendable (depending on the test needs and configuration):

    output "domain_ips" {
        value = "${libvirt_domain.domain-sle.*.network_interface.0.addresses}"
    }


### Authors
Jose Lausuch <jalausuch@suse.com>,  *QA Engineer at SUSE*


[trfm1]: <https://www.terraform.io/intro/index.html>
[trfm2]: <https://www.terraform.io/docs/providers/>
[trfm3]: <https://github.com/dmacvicar/terraform-provider-libvirt>
