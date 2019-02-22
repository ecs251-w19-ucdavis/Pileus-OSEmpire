# Pileus Weekly Progress #1

**Done last week:**

Shahbaz:

* Completed basic implementation of Database class that store and retrieve on Json file is done.
* Completed basic implementation of StorageNode as RPYC service that clients can connect to. Also expose put and get functions.

Greg:

* Began implementation of Client class with basic function prototypes
  * create table, delete table, put, get, open table, begin session, end session. 
* Completed basic implementation of SLA class
  * defines a consistency, latency, and utility
* Completed basic implementation of Session class
  * connect to server, disconnect from server, keep history of puts and gets during session for use with certain consistency levels

Nader:

* Began implementation of the three Monitor functions that return probability estimates based on the recorded information on the client.
  * PNodeCons (node, consistency, key) returns a conservative estimate of the probability that the given storage node is sufficiently up-to-date to provide the given consistency guarantee for the given key.
  * PNodeLat (node, latency) returns an estimate of the probability that the node can respond to Gets within the given response time.
  * PNodeSla (node, consistency, latency, key) returns an estimate of the probability that the given node can meet the given consistency and latency for the given key.


**Doing this week:**

Shahbaz:

* Simple implementation of ReplicationAgent class that periodically push data from primary storage node to secondary nodes.
* Currently, only one primary node is implemented and tested. Cases with several secondary storage node should be fully implemented and tested.

Greg:

* Finish basic implementation of Client class.
  * Store SLA as a list of SLA objects
* Implement Get function which chooses among SLAs based on monitor information. I.e. For each item in the list of SLAs, predict latency and consistency. Based on these predictions, choose among the SLAs based on utility.

Nader:

* Completing the three monitor operations.
* Include the RTT and timestamps logic in the clients Gets and Puts to get the necessary informations for monitoring.
* Start running our system on AWS.

**Issues/Problems:**

* Where to implement timestamp synching? Should client provide timestamp or server?

**Link to Trello Board**

[ECS_251_Pileus_Design_Board](https://trello.com/b/6lscmOq9/pileus)
