# Pileus Weekly Progress #1

**Done last week:**

Shahbaz:

* Databased class was changed to support multiple tables. Now, it also stores a metadata file that contains each tables last version in the local database. During database synchronization, replication agents only update tables that a newer version is available in primary to avoid uneccessary traffic.
* StorageNode was changed to handle and control replication agent itself.
* High timestamp is implemented according to the paper.
* Table-based actions, such as create_table and delete_table, were added to the StorageNode.
* To improve performance and flexibility, in the new implementation, secondy node's replication agents will pull updates from primary node instead of the previous case where pimary node push updates to the secondary nodes.

Greg:


Nader:

* Refining the design of monitors functions that measure the likelihood that the specified SLA meets its consistency and latency requirements.
* Start testing the plateform on AWS instances.


**Doing this week:**

Shahbaz:

* Implementing put log and sending put log to secondary storage nodes (instead of the whole tables that were changed) to improve the efficiency of replication agent update process.

Greg:

Nader:

* Modifying the get function to compute and return the round trip time (RTT) and other necessary information for monitor to function. 


**Issues/Problems:**


**Link to Trello Board**

[ECS_251_Pileus_Design_Board](https://trello.com/b/6lscmOq9/pileus)
