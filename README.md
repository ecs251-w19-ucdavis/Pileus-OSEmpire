# Pileus
Consistency-based SLA Could System by Microsoft
# Source code structure
**src directory**
* contains python files for both client side and server side code

**src/client**
* contains python files that are expected to be used on the client side.

**src/client/Consistency.py**
* Defines the consistency class, which is used in created and working with 
any of the six defined consistency levels. Provides methods to get and set
minimum acceptable timestamp.

**src/client/SLA.py**
* Defines the SLA class, which is used in creating and working with Service
Level Agreements, as defined in this system. Each SLA object consists of a 
consistency object, a latency constraint and a utility. Provides methods to 
get and set consistency, utility and latency. A group of SLA objects is 
expected to be combined into a list and provided as input to client object.

**src/client/Session.py**
* Defines the Session class, which is used in starting a connection to the 
storage node and facilitating get() and put() requests from the client. Also,
stores the put and get history of the client, on a per key level, during the 
session, as well the continually updating maximum timestamp during the 
session. This information is later used in facilitating node selection in 
get() operation.

**src/client/Monitor.py**
* Defines the Monitor class, which is used by the client to deposit and 
withdraw information regarding latency and consistency of each node. It also
contains a method for connecting to all known servers and getting latency 
and consistency information without the client. Provides functions 
p_node_cons(), p_node_lat(), and p_node_sla(), which are used by the client 
to determine which node to send the get() requests to.

**src/client/Client.py**
* Defines the Client class, which uses all of the above mentioned classes to
facilitate get() and put() requests.

**src/server**
* contains python files that are expected to be used on the server side.

# Server Side Implementation
There are Three main classes on the server side:

**src/server/Database**
* This a basic implementation of a key-value database. It stores (key, value, timestamps) tuples in tables. It also has a metadata to store table update information and a transaction log which record every modifying operations on database.

**src/server/StorageNode** 
* It is a RPyC service to handle requests from users. It is an interface between users and database. It also initiates replication agent to handle periodic updates.

**src/server/ReplicationAgent** 
* A basic implementation of a service that periodically update secondary storage node's database from primary storage node.

# How to run primary/secondary servers
To run a server, you need to run the StorageNode.py python file. It will instantiate Database and Replication Agent as well. The default parameters are set to make the running server as a Primary node. To make the node as a secondary node, you need to change the isPrimary variable in the StorageNode.py file to false.

# Correctness Experiment
To check the correctness of the whole system, you can run the Client.py. The main() function in Client.py constructs multiple SLA objects, incorporating all of the six consistency categories provided. Along with the consistency, each SLA also has a latency in seconds and a utility value. All of the SLAs are combined into a list and provided as input to the Client. The Client then makes multiple put requests and some get requests. For each get request, we provide a verbose mode for the Client and the Monitor. By setting debug_mode=True in the object constructor of Client and Monitor, we can receive useful information about the results. This information includes: what was the target node for each get() request, what were the predictions for each node and SLA combination, what were the best nodes or node, which node was each get() request sent to, how long did the actual get() request take, which SLAs were determined to have been met after the get() requst, and more.

# Benchmarking Application
1. To run, you need to install the following dependencies:

   ``` bash
    $ tabulate
    $ clint
    $ rpyc
    $ docopt
    $ seaborn
    ```

2. Set up a Storage Node as Primary (You can also set any number of Secondary replicas). Update the configuration file with their public IP addresses. 
    
3. Run the application!

    ```
    $ cd /src/client
    $ python Benchmark.py [options]
    ```
    
    Examples:
    
    ``` bash
    # Benchmark alternates between 10 reads and writes, with randomly ordered reads, sleep mode activated
    $ python Benchmark.py -v -s --trials=10 --random --no-split
    
    # Benchmark with 10 reads and writes, each with two 1000 character fields
    $ python Benchmark.py -v --trials=100 --length=1000 
    
    ```

    * General usage information and options: `$ python Benchmark.py -h`:
    ``` bash
    Usage:
        main.py [options]

    Options:
        -h --help           Show this help screen
        -v                  Show verbose output from the application
        -V                  Show REALLY verbose output, including the time
                                from each run
        -s                  Sleep mode (experimental) - sleeps for 1/20 (s)
                                between each read and write
        -r --random         Activates random mode, where reads are taken
                                randomly from the DB instead of sequentially
        --no-csv            App will not generate a CSV file with the raw data
        --no-report         Option to disable the creation of the report file
        --no-split          Alternate between reads and writes instead of all
                                writes before reads
        --length=<n>        Specify an entry length for reads/writes
                                [default: 10]
        --trials=<n>        Specify the number of reads and writes to make to
                                the DB to collect data on [default: 1000]
    ```
