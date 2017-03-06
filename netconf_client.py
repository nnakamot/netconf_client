#! /usr/bin/env python

#
# Copyright (c) 2017 by Norio Nakamoto
# All rights reserved.
#

# - This script connects with NETCONF agent using ncclient library

 
import time, sys, os
import optparse
import cmd
import dircache

from netconf_client_lib import *

DEFAULT_LOG = './netconf_client_log.txt'
DEFAULT_RES = './netconf_response.txt'

MSG_SENT = '\n--------------- Sent to NETCONF agent ----------------'
MSG_RECIEVED = '\n----------- Received from NETCONF agent --------------'
MSG_SEPARATE = '------------------------------------------------------'

logf = None

def print_log(msg, no_cr=False, log_only=False):
    global logf

    if not log_only:
        if no_cr:
            print msg,
            sys.stdout.flush()
        else:
            print msg
    logf.write(msg + '\n')

class CLI(cmd.Cmd):
    def __init__(self, nc):
        cmd.Cmd.__init__(self)
        self.prompt = "netconf> "
        self.intro = "\nHello. You have connected to NETCONF agent.\n\n" + \
                     "Type 'help' or '?' to see the available commands"
        self.doc_header = "Type 'help <command>' to see the help for each command:"
        self.ruler = "-"
        self.nc = nc
    def emptyline(self):
        pass
    def do_EOF(self, args):
        '''End this program by entering ctrl+d'''
        self.stdout.write("\nExiting...\n\n")
        return 1
    def do_bye(self, args):
        '''Close session and end this program'''
        self.stdout.write("Exiting...\n\n")
        # User wants to quit. Send <close-session> request 
        if self.nc.close():
            success = True
        else:
            success = False
        return 1
    def do_quit(self, args):
        '''Close session and end this program'''
        self.do_bye(args)
        return 1
    def do_exit(self, args):
        '''Close session and end this program'''
        self.do_bye(args)
        return 1
    def do_comment(self, args):
        '''Write comment in the log file'''
        print_log('\n### ' + args + ' ###')

    def do_get_cfg_all(self, line):
        '''Send get-config request without filter (request entire running datastore)'''
        self.nc.get_config()
        print_log(MSG_SENT) 
        print_log(self.nc.request)
        print_log(MSG_SEPARATE)

        print_log(MSG_RECIEVED) 
        print_log(self.nc.reply)
        print_log(MSG_SEPARATE)

    def do_get_cfg_filter(self, path):
        '''
Send get-config request with filter\nusage: get_cfg_filter <file containing filter data>
        '''
        if path is None or len(path) == 0:
            print_log("ERROR: Please specify a file containing filer data.")
            return

        # Get filter data
        filter = get_data_from_user(path)
        if filter is not None and len(filter) > 0:
            self.nc.get_config(filter)
        else:
            print_log("ERROR: Filter data is empty!")
            return

        print_log(MSG_SENT) 
        print_log(self.nc.request)
        print_log(MSG_SEPARATE)

        print_log(MSG_RECIEVED) 
        print_log(self.nc.reply)
        print_log(MSG_SEPARATE)

    def do_get_filter(self, path):
        '''Send get request with filter\nusage: get_filter <file containing filter data>'''
        # Get filter data
        if path is None or len(path) == 0:
            print_log("ERROR: Please specify a file containing filer data.")
            return

        filter = get_data_from_user(path)
        if filter is not None and len(filter) > 0:
            self.nc.get(filter)
        else:
            print_log("ERROR: Filter data is empty!")
            return

        print_log(MSG_SENT) 
        print_log(self.nc.request)
        print_log(MSG_SEPARATE)

        print_log(MSG_RECIEVED) 
        print_log(self.nc.reply)
        print_log(MSG_SEPARATE)

    def do_edit_cfg(self, path):
        '''Send edit-config request\nusage: edit_cfg <file containing config data>'''
        # Get config data
        if path is None or len(path) == 0:
            print_log("ERROR: Please specify a file containing config data.")
            return

        config = get_data_from_user(path)
        if config is not None and len(config) > 0:
            self.nc.edit_config(config)
        else:
            print_log("ERROR: Config data is empty!")
            return

        print_log(MSG_SENT) 
        print_log(self.nc.request)
        print_log(MSG_SEPARATE)

        print_log(MSG_RECIEVED) 
        print_log(self.nc.reply)
        print_log(MSG_SEPARATE)

    def do_commit(self, path):
        '''commit'''
        self.nc.commit()
        print_log(MSG_SENT) 
        print_log(self.nc.request)
        print_log(MSG_SEPARATE)

        print_log(MSG_RECIEVED) 
        print_log(self.nc.reply)
        print_log(MSG_SEPARATE)

    def do_discard(self, path):
        '''discard-changes'''
        self.nc.discard()
        print_log(MSG_SENT) 
        print_log(self.nc.request)
        print_log(MSG_SEPARATE)

        print_log(MSG_RECIEVED) 
        print_log(self.nc.reply)
        print_log(MSG_SEPARATE)

    def do_get_capabilities(self, path):
        '''get capability list'''
        # simply return capabilities saved by ncclient from hello message 
        for cap in self.nc.session.server_capabilities:
            print_log(cap)

    def do_get_schema_list(self, path):
        '''get schema list'''
        self.nc.schema_list()
        print_log(MSG_SENT) 
        print_log(self.nc.request)
        print_log(MSG_SEPARATE)

        print_log(MSG_RECIEVED) 
        print_log(self.nc.reply)
        print_log(MSG_SEPARATE)

    def do_send_request(self, path):
        '''
Send a request in a file\nusage: send_request <file containing a request>
        '''
        if path is None or len(path) == 0:
            print_log("ERROR: Please specify a file containing a request.")
            return

        # Get a request 
        request = get_data_from_user(path)
        if request is not None and len(request) > 0:
            self.nc.dispatch(request)
        else:
            print_log("ERROR: Config data is empty!")
            return

        print_log(MSG_SENT) 
        print_log(self.nc.request)
        print_log(MSG_SEPARATE)

        print_log(MSG_RECIEVED) 
        print_log(self.nc.reply)
        print_log(MSG_SEPARATE)

    # These are for command line completion
    def complete_get_cfg_filter(self, text, line, begidx, endidx):
        return comp_path(text, line, begidx, endidx)
    def complete_get_filter(self, text, line, begidx, endidx):
        return comp_path(text, line, begidx, endidx)
    def complete_edit_cfg(self, text, line, begidx, endidx):
        return comp_path(text, line, begidx, endidx)
    def complete_send_request(self, text, line, begidx, endidx):
        return comp_path(text, line, begidx, endidx)


def comp_path(text, line, begidx, endidx):
    """ auto complete for file name and path. """
    line = line.split()
    if len(line) < 2:
        filename = ''
        path = './'
    else:
        path = line[1]
        if '/' in path:
            i = path.rfind('/')
            filename = path[i+1:]
            path = path[:i]
        else:
            filename = path
            path = './'

    ls = dircache.listdir(path)
    ls = ls[:] # for overwrite in annotate.
    dircache.annotate(path, ls)
    if filename == '':
        return ls
    else:
        return [f for f in ls if f.startswith(filename)]

def get_data_from_user(file):
    if len(file) == 0:
        return False

    try:
        req = open(file, 'r')
    except:
        print_log("ERROR: Unable to open " + file + "!")
        return None

    print_log("\nFile specified: " + file)
    return req.read()

def interacive_mode(nc):
    # Now loop for sneding request and receiving response     
    terminate = False 
    CLI(nc).cmdloop()

def oneline_mode(nc, request, response, dump):
    try:
        req = open(request, 'r')
    except:
        print "ERROR: Unable to open " + request + "!"
        return

    if response is not None:
        res_file = response
    else:
        res_file = DEFAULT_RES

    try:
        res = open(res_file, 'w')
    except:
        print "ERROR: Unable to open " + res_file + "!"
        return

    req_str = req.read()
    nc.dispatch(req_str)

    if dump:
        print_log(MSG_SENT) 
        print_log(nc.request)
        print_log(MSG_SEPARATE)
        print_log(MSG_RECIEVED) 
        print_log(nc.reply)
        print_log(MSG_SEPARATE)
    else:
        print_log(MSG_SENT, False, True) 
        print_log(nc.request, False, True)
        print_log(MSG_SEPARATE, False, True)
        print_log(MSG_RECIEVED, False, True) 
        print_log(nc.reply, False, True)
        print_log(MSG_SEPARATE, False, True)

    res.write(nc.reply)
    res.write('\n')

    if ('edit-config' in req_str or 'copy-config' in req_str) and \
        '<ok/>' in nc.reply:
        # edit-config so send commit operation implicitly
        nc.commit()

        if dump:
            print_log(MSG_SENT) 
            print_log(nc.request)
            print_log(MSG_SEPARATE)
            print_log(MSG_RECIEVED) 
            print_log(nc.reply)
            print_log(MSG_SEPARATE)
        else:
            print_log(MSG_SENT, False, True) 
            print_log(nc.request, False, True)
            print_log(MSG_SEPARATE, False, True)
            print_log(MSG_RECIEVED, False, True) 
            print_log(nc.reply, False, True)
            print_log(MSG_SEPARATE, False, True)

        res.write(nc.reply)
        res.write('\n')

    print "\nThe response is saved in '" + res_file + "'\n"


def nf_client(host, port=None, device=None, user=None, passwd=None, log=None,
        request=None, response=None, dump=False, debug=False):
    global logf

    # open log file 
    if log is not None:
        logfile = log
    else:
        logfile = DEFAULT_LOG

    try:
        logf = open(logfile, 'w')
    except:
        print "ERROR: Unable to open " + logfile + "!"
        return None

    # Create NetconfClient class instance and connect to netconf agent  
    nc = NetconfClient(host, port, device, 'ssh', user, passwd, debug)
    if nc is None or (nc is not None and not nc.connected):
        print_log("ERROR: Failed to connect netconf agent!")
        return False

    if request is not None:
        # non-interacive mode
        oneline_mode(nc, request, response, dump)
    else:
        # Go interacive
        interacive_mode(nc)

    print "The operation log is saved in '" + logfile + "'\n"

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('--host', help='IP address to connect to')
    parser.add_option('--port', type=int, 
                        help='Port number that NETCONF agent listens')
    parser.add_option('--device', 
                        help='Connecting device type (default: iosxr)')
    parser.add_option('--user', help='User name to login')
    parser.add_option('--passwd', help='Password for user login')
    parser.add_option('--debug', action='store_true', default=False,
                        help='Turn on debug print', )
    parser.add_option('--log', help='File to save operation log')
    parser.add_option('--request', help='File to provide a request to send')
    parser.add_option('--response', help='File to save the response message')
    parser.add_option('--dump', action='store_true', default=False,
                        help='Turn on terminal output', )
    args, remainder = parser.parse_args()

    nf_client(args.host, args.port, args.device, args.user, args.passwd, 
            args.log, args.request, args.response, args.dump, args.debug)


