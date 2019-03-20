# Pileus
Consistency-based SLA Could System by Microsoft. Based on "Consistency-based service level agreements for cloud storage" paper.
# Server Side Implementation
There are Three main classes on the server side:

Database: This a basic implementation of a key-value database. It stores (key, value, timestamps) tuples in tables. It also has a metadata to store table update information and a transaction log which record every modifying operations on database.
StorageNode: It is a RPyC service to handle requests from users. It is an interface between users and database. It also initiates replication agent to handle periodic updates.
ReplicationAgent: A basic implementation of a service that periodically update secondary storage node's database from primary storage node.

# How to run primary/secondary servers
To run a server, you need to run the StorageNode.py python file. It will instantiate Database and Replication Agent as well. The default parameters are set to make the running server as a Primary node. To make the node as a secondary node, you need to change the isPrimary variable in the StorageNode.py file to false.
