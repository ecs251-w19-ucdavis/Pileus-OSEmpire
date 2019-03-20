# Pileus
Consistency-based SLA Could System by Microsoft. Based on "Consistency-based service level agreements for cloud storage" paper.
# How to run primary/secondary servers
To run a server, you need to run the StorageNode.py python file. It will instantiate Database and Replication Agent as well. The default parameters are set to make the running server as a Primary node. To make the node as a secondary node, you need to change the isPrimary variable in the StorageNode.py file to false.
