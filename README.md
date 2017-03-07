# netconf_client
Python script of simple netconf client using ncclient API
The script works as netconf client that can connect a remote netconf agent.
It can be used either one-line-command type of tool, or shell-like interactive tool.

[Prerequisites]
  - ncclient library (0.4.7 or newer required to use netconf v1.1 protocol)
  - netconf_client_lib.py must be in python path or placed together with netconf_client.py

[Usage]
Usage: netconf_client.py [options]

Options:
  -h, --help           show this help message and exit
  --host=HOST          IP address to connect to
  --port=PORT          Port number that NETCONF agent listens
  --device=DEVICE      Connecting device type (default: iosxr)
  --user=USER          User name to login
  --passwd=PASSWD      Password for user login
  --debug              Turn on debug print
  --log=LOG            File to save operation log
  --request=REQUEST    File to provide a request to send
  --response=RESPONSE  File to save the response message
  --dump               Turn on terminal output

[One-line Command Execution Mode]
- Run the script with '--request' (i.e. specifying a netconf request to run) will run the script as one-liner
   Ex.
     netconf_client.py --host=HOST --user=USER --request <path-to-your-request-file> 
     Enter password: 

    --------------- Sent to NETCONF agent ----------------
        <get-config>
            <source>
                <running/>
            </source>
         </get-config>

    ------------------------------------------------------

    ----------- Received from NETCONF agent --------------
    <?xml version="1.0" encoding="UTF-8"?><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
      <host-names xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-shellutil-cfg">
          <host-name>ThisIsTheRouter</host-name>
      </host-names>
    ...
       </interface>
      </interfaces>
     </data>

    ------------------------------------------------------

    The response is saved in './netconf_response.txt'

    The operation log is saved in './netconf_client_log.txt'
    
[Interactive Mode]
- Run the script without '--request' and shell-like client menu starts
   Ex.
     # netconf_client.py --host=HOST --user=USER --dump
     Enter password: 

     Hello. You have connected to NETCONF agent.

     Type 'help' or '?' to see the available commands
     netconf> help

     Type 'help <command>' to see the help for each command:
     -------------------------------------------------------
     EOF      commit    exit              get_cfg_filter   help        
     bye      discard   get_capabilities  get_filter       quit        
     comment  edit_cfg  get_cfg_all       get_schema_list  send_request

     netconf> 

Note: <rpc> tags are not needed in the netconf request you specify
