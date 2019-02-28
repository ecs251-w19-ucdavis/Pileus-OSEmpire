# Pileus Weekly Progress #2

**Done last week:**

Shahbaz:

* Databased class was changed to support multiple tables. Now, it also stores a metadata file that contains each tables last version in the local database. During database synchronization, replication agents only update tables that a newer version is available in primary to avoid uneccessary traffic.
* StorageNode was changed to handle and control replication agent itself.
* High timestamp is implemented according to the paper.
* Table-based actions, such as create_table and delete_table, were added to the StorageNode.
* To improve performance and flexibility, in the new implementation, secondy node's replication agents will pull updates from primary node instead of the previous case where pimary node push updates to the secondary nodes.

Greg:

* Updated Put() in Client to pass proper values to server, measure
 latency, and provide node latency information to Monitor on success.
* Updated Get() in Client to pass proper values to server, measure 
latency, extract data from server response object, and pass latency and 
high-timestamp of node to Monitor.
* Implemented basic Monitor class, which will be modified later.
* Added new list variable to List class to store the ip-addresses of all
 available nodes. 

Nader:

* Refining the design of monitors functions that measure the likelihood that the specified SLA meets its consistency and latency requirements.
* Start testing the platform on AWS instances.


**Doing this week:**

Shahbaz:

* Implementing put log and sending put log to secondary storage nodes (instead of the whole tables that were changed) to improve the efficiency of replication agent update process.

Greg:

* Implement a better system for defining a consistency level, 
specifically providing a minimum acceptable high-timestamp for each.
* Complete full Get() function.
* Figure out a way to tie consistency with a key. i.e., can this node 
meet the consistency requirements for this specific key? Currently, 
consistency is considered equal across an entire node, regardless of 
key. This detail is not clear enough in the paper.
* The Get() function should also return which of the SLAs were met and 
which were not. Need to implement this.

Nader:

* Modifying the get function to compute and return the round trip time (RTT) and other necessary information for monitor to function. 


**Issues/Problems:**


**Link to Trello Board**

[ECS_251_Pileus_Design_Board](https://trello.com/b/6lscmOq9/pileus)
