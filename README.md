# smokejumper
A collection of load and scale testing tools for kubernetes  

# Testing order

1. Deploy Bare Metal Cluster
2. Deployed MachineConfig with Multipah configuration in the nodes
3. Deployed CSI Operator
   - 3.1 Configured Infinidat StorageClass (Default, permissions)
   - 3.2 Configure Infinidat SnapshotClass
4. Configured Registry
5. Deployed the OpenShift Virtualization Operator
   - 5.1 Created the Virtualization instance (Enable VM creation)
6. Deployed the NMState Operator
   - 6.1 Created a NMState DNS configuration for the nodes (Due to long DNS search domain entries; limit 251 chars)
7. Deployed kube-burner

# Helpful links
Some work pulled from:
https://hackmd.io/@johnsimcall/BkElnsvUA

FIO Cheat Sheet:
https://gist.github.com/githubfoam/a678cfc813c7ede6ca9ecb93e34edd8e

IOStat Cheat Sheet:
https://www.golinuxcloud.com/iostat-command-in-linux/
