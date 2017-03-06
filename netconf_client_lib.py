#
# NETCONF client class using ncclient 
#
# Note that this script is aimed to connect netconf v1.1 agent and make 
# sure that your ncclient version supports v1.1 (i.e. version 0.4.7 or newer)
#
import sys, os
import logging
import getpass

#logging.basicConfig()
#logging.getLogger("ncclient.transport.ssh").setLevel(logging.DEBUG)
#logging.getLogger("ncclient.transport.session").setLevel(logging.DEBUG)
#logging.getLogger("ncclient.operations.rpc").setLevel(logging.DEBUG)

# This is to specify ncclient that may be installed locally
#sys.path.append('<path-to-ncclient-module>')

import ncclient

version = ncclient.__version__

if version[0] == 0 and \
        (version[1] < 4 or (version[1] == 4 and version[2] < 7)):
    # This version does not support netconf v1.1
    sys.exit('Your ncclient version (%s.%s.%s) does not support netconf ' \
             % (version[0], version[1], version[2]) + \
             'v1.1.\nPlease use version 0.4.7 or newer.')

from ncclient import manager
from ncclient.xml_ import *

# Global variables
CLOSE = """
    <close-session/>
"""

GET_CONFIG = """
    <get-config>
        <source>
            <running/>
        </source>
    </get-config>
"""

COMMIT = """
<commit/>
"""

DISCARD = """
<discard-changes/>
"""

global_debug = False

def debug_print(msg, no_cr=False):
    global global_debug
    if global_debug:
        if no_cr:
            print msg,
        else:
            print msg

def connect_ssh(host, port, user, passwd, device):
    if port is None:
        port = 830

    debug_print("\tConnecting to netconf agent (%s) over ssh... " % host,
                True)
    if device is None:
        device_name = 'iosxr'
    else:
        device_name = device

    try: 
        session = manager.connect(host = host, 
                                  port = port, 
                                  username = user, 
                                  password = passwd,
                                  device_params = {'name':device_name})
    except Exception, err:
        debug_print("failed (%s)\n" % str(err))
        return None

    session.timeout = 3600
    debug_print("success")
    return session

class NetconfClient():
    """
    netconf client object class
    """
    transport = 'ssh'
    p = None
    session = None
    hello = ''
    request = ''
    reply = ''
    connected = False

    def __init__(self, host, port=None, device=None, transport=None, 
                user=None, passwd=None, debug=False):
        """
        Init method of this class
        This will create a new instance and create a new session with netconf 
        agent
        """
        global global_debug
        global_debug = debug

        if host is None:
            print "ERROR: Agent address not provided!"
            return None

        if passwd is None:
            # Try to get password from terminal if not given
            password = getpass.getpass('Enter password: ')
        else:
            password = passwd

        if transport is not None:
            self.transport = transport

        if self.transport == 'ssh':
            self.session = connect_ssh(host, port, user, password, device)
            if self.session is not None:
                # connection was success
                self.connected = True

    def close(self): 
        debug_print("- Closing netconf session...")
        return self.send_and_receive(CLOSE)

    def get_config(self, filter=None):
        debug_print("Getting config...")

        if filter is None:
            request = GET_CONFIG
        else:
            if '<get-config>' in filter:
                request = filter
            else:
                request = """
<get-config>
<source><running/></source>
<filter>
"""
                request += filter
                request += """
</filter>
</get-config>
"""

        return self.send_and_receive(request)

    def get(self, filter=None):
        debug_print("- Getting data...")

        if filter is None:
            print "XR netconf agent does not support get request without filter!"
            return False

        if '<get>' in filter:
            get_req = filter
        else:
            get_req = """
<get>
<filter>
"""
            get_req += filter
            get_req += """
</filter>
</get>
"""

        return self.send_and_receive(get_req)

    def edit_config(self, config):
        debug_print("- Editing config...")
        if '<edit-config>' in config:
            # edit-config tag is already included
            edit_config = config
        else:
            edit_config = """
<edit-config>
<target><candidate/></target>
<config>
"""
            edit_config += config
            edit_config += """
</config>
</edit-config>
"""

        return self.send_and_receive(edit_config)

    def commit(self):
        debug_print("- Commiting config...")
        return self.send_and_receive(COMMIT)

    def discard(self):
        debug_print("- Discarding changes...")
        return self.send_and_receive(DISCARD)

    def schema_list(self):
        debug_print("- Getting schema list...")

        get_schemas = """
<get>
 <filter type="subtree">
  <netconf-state xmlns=
                  "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
   <schemas/>
  </netconf-state>
 </filter>
</get>
"""

        return self.send_and_receive(get_schemas)

    def capability_list(self):
        debug_print("- Getting capability list...")

        get_caps = """
<get>
 <filter type="subtree">
  <netconf-state xmlns=
                  "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
   <capabilities/>
  </netconf-state>
 </filter>
</get>
"""

        return self.send_and_receive(get_caps)

    def dispatch(self, request):
        debug_print("- Sending a request to netconf agent... ", True)

        return self.send_and_receive(request)

    # These are common functions
    def send_and_receive(self, request):
        debug_print("- Sending a request to netconf agent...", True)

        if self.transport == 'ssh':
            # send a request through ncclient 
            self.request = request
            try:
                result = self.session.dispatch(to_ele(request))
            except Exception, err:
                debug_print("failed (%s)\n" % str(err))
                self.reply = to_xml(err.xml)
                return False
                #return (False, err)

            if (result.ok):
                if result.data is not None:
                    self.reply = to_xml(result.data)
                else:
                    self.reply = 'ok'
                debug_print("success")
            else: 
                self.reply = to_xml(result.xml)
                debug_print("failed")

            return True

