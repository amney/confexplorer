# confexplorer

## Installation

confexplorer requires the following packages

* Flask 
* Requests
    
Install them using ``pip install -r requirements.txt``

## Running

Once the requirements have been installed launch the Flask server:

    python explorer.py --help
    usage: explorer.py [-h] -u URL -l LOGIN -p PASSWORD [-d DEPTH]

    ACI Configuration Visualisers

    optional arguments:
      -h, --help            show this help message and exit
      -u URL, --url URL     APIC IP address.
      -l LOGIN, --login LOGIN
                            APIC login ID.
      -p PASSWORD, --password PASSWORD
                            APIC login password.
      -d DEPTH, --depth DEPTH
                            Maximum config recursion depth. DEFAULT=2
                            
                            
For example:

    python explorer.py -u https://apic-1/ -l admin -p apicpassword
    
After the webserver has started you will need to open the visualisation in your web browser

    http://localhost:5000/
  
## How does it work?

confexplorer starts a flask webserver and listens on ``127.0.0.1:5000`` 

When a client connects it will pull the entire configuration tree from the APIC
specified when launching the script. The configuration is then manipulated to fit
the format expected by the d3.js visualisation library. This data is then sent to
the browser which uses d3.js to generate a pack diagram.

## Demo
    
![Demo](http://gfycat.com/CooperativeClearcutGhostshrimp)
  
