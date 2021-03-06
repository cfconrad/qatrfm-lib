#!/usr/bin/env python

import base64
import json

def generate_guest_exec_str(domain, cmd):
    str = ("virsh -c qemu:///system qemu-agent-command --domain {} --cmd "
        "\'{{ \"execute\": \"guest-exec\", \"arguments\": {{ \"path\": "
        .format(domain))

    if ' ' in cmd:
        cmds = cmd.split(' ')
        str += '\"{}\", \"arg\": ['.format(cmds[0])
        args = ''
        i = 1
        while i < len(cmds):
            str += '\"{}\"'.format(cmds[i])
            if (i < len(cmds) - 1): str += ', '
            i += 1
        str += '], '
    else:
        str += '\"{}\", '.format(cmd)
    str += '\"capture-output\": true }}\''
    return str


def generate_guest_exec_status(domain, pid):
    return 'virsh -c qemu:///system qemu-agent-command --domain {} --cmd \'{{ \"execute\": \"guest-exec-status\", \"arguments\": {{ \"pid\": {} }}}}\''.format(domain, pid)

def get_pid(str):
    return json.loads(str)["return"]["pid"]

def get_ret_code(str):
    return json.loads(str)["return"]["exitcode"]

def process_is_exited(str):
    if (json.loads(str)["return"]["exited"]): return True
    return False

def get_output(str, field = 'out-data'):
    output = ''
    try:
        output = base64.b64decode(json.loads(str)["return"][field]).decode("utf-8") 
    except:
        pass
    return output