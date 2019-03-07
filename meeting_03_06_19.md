# Pileus Weekly Progress #1

**Done last week:**

Shahbaz:

* Completed replication log on Database class.
* Completed update using replication log and table-based as a backup update method.

Greg:

* Added new class Consistency, which holds type, minimum_acceptable_consistency,
 and time_bound for each type of consistency used in the system.
 * Added two list variables to Session class to keep track of Put and Get 
 requests.
 * Added variable to Session to keep track of the largest known timestamp
 * Added functions to Session to keep update the three new variables 
 mentioned above
 * Modified SLA class to use new Consistency class and removed Consistency 
 string names from SLA class
 * Updated Put, Get methods in Client class to pass values to the session 
 object.

Nader:

* Finishing the implementation of monitoring functionalities.
* Configuring AWS instances for evaluation (may switch to Digital Ocean)

**Doing this week:**

Shahbaz:

* Implementing Open method and a method to lock tables and metadatas.

Greg:

Nader:

* Build a small benchmark for evaluation (similar to YCSB).
* Completing setting up the evaluation plateform.
* Extracting and plotting results.

**Issues/Problems:**

**Link to Trello Board**

[ECS_251_Pileus_Design_Board](https://trello.com/b/6lscmOq9/pileus)
