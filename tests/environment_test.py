#!/usr/bin/env python3
#
# Copyright © 2019 SUSE LLC
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

import pytest
import tempfile
import shutil
import re
import paramiko

from unittest import mock

from qatrfm.environment import TerraformEnv
from qatrfm.domain import Domain
from qatrfm.utils.libutils import execute_bash_cmd

pytest.TFVARS = {"var1=val1", "var2=val2", "var3=val3"}
pytest.FILENAME = 'file.tf'


class TestTerraformEnv(object):
    """ Test TerraformEnv """

    TMP_FOLDER = '/tmp/folder'
    EXEC_RETURN = '10.1.0.'

    @mock.patch('tempfile.mkdtemp', return_value=TMP_FOLDER)
    @mock.patch('shutil.copy')
    @mock.patch('qatrfm.utils.libutils.execute_bash_cmd',
                return_value=[0, EXEC_RETURN])
    @pytest.fixture
    def mocked_TerraformEnv(self, mock_mkdtemp, mock_copy, mock_exec):
        return TerraformEnv(pytest.TFVARS)

    @mock.patch('tempfile.mkdtemp', return_value=TMP_FOLDER)
    @mock.patch('shutil.copy')
    @mock.patch('qatrfm.utils.libutils.execute_bash_cmd',
                return_value=[0, EXEC_RETURN])
    @pytest.fixture
    def mocked_TerraformEnv_file(self, mock_mkdtemp, mock_copy, mock_exec):
        return TerraformEnv(pytest.TFVARS, pytest.FILENAME)

    def test_init_only_vars(self, mocked_TerraformEnv):
        assert isinstance(mocked_TerraformEnv, TerraformEnv)
        assert mocked_TerraformEnv.net_octet == 0
        assert re.match(
            '(-var \'var\d=val\d\' ){3}', mocked_TerraformEnv.tf_vars)
        assert mocked_TerraformEnv.tf_file is None
        assert mocked_TerraformEnv.snapshots is False

    def test_init_no_vars(self):
        with pytest.raises(TypeError):
            TerraformEnv()

    def test_init_with_file(self, mocked_TerraformEnv_file):
        assert mocked_TerraformEnv_file.tf_file == pytest.FILENAME
