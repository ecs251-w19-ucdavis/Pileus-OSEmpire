# Pileus
Consistency-based SLA Could System by Microsoft
# Source code scructure
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

Database: This a basic implementation of a key-value database. It stores (key, value, timestamps) tuples in tables. It also has a metadata to store table update information and a transaction log which record every modifying operations on database.

StorageNode: It is a RPyC service to handle requests from users. It is an interface between users and database. It also initiates replication agent to handle periodic updates.

ReplicationAgent: A basic implementation of a service that periodically update secondary storage node's database from primary storage node.

# How to run primary/secondary servers
To run a server, you need to run the StorageNode.py python file. It will instantiate Database and Replication Agent as well. The default parameters are set to make the running server as a Primary node. To make the node as a secondary node, you need to change the isPrimary variable in the StorageNode.py file to false.