import paramiko, sys
from forward import forward_tunnel

remote_host = "127.0.0.1"
remote_port = 3306
local_port  = 3306
ssh_host    = "teatrocambiano.sytes.net"
ssh_port    = 22

user     = "ltc"
password = "ltc"

transport = paramiko.Transport((ssh_host, ssh_port))

# Command for paramiko-1.7.7.1
transport.connect(hostkey  = None,
                  username = user,
                  password = password,
                  pkey     = None)

try:
    forward_tunnel(local_port, remote_host, remote_port, transport)
except KeyboardInterrupt:
    print ('Port forwarding stopped.')
    sys.exit(0)