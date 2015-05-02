# Cluster provisioning tool

A cluster automation tool which creates multi node hadoop clusters and sharded MongoDB clusters on various cloud platforms. The supported platforms are Digital Ocean, Amazon web services and OpenStack.

## Installation

    # Install Dependencies
    $ sudo pip install -r requirements.txt
    $ cp cat-template.conf cat.conf
  
  # Enter Authentication tokens and customize the configurations.
  
## How to use

    $ python main.py --app <appname> --provider <provider> --nodes <noofnodes>
    # Use python main.py -h for help.
  
    usage: main.py [-h] [--nodes NODES] --app [{hadoop,mongodb,none}] --provider[{digitalocean,openstack,aws}]

    optional arguments:
    -h, --help                                    show this help message and exit
    --nodes NODES                                 Number of nodes in the cluster. Default is 1
    --app [{hadoop,mongodb,none}]                 Application to be installed
    --provider [{digitalocean,openstack,aws}]     Choose the Cloud provider
