# smokejumper
A collection of load and scale testing tools for kubernetes  

# Build order

1. Deploy Bare Metal Cluster
2. Deployed MachineConfig with Multipah configuration in the nodes
3. Deployed CSI Operator
   - 3.1 Configured Infinidat StorageClass (Default, permissions)
   - 3.2 Configure Infinidat SnapshotClass
4. Configured Registry
5. Set RHCOS "HighBurst"
6. Set "Max LUN IDs"
7. Deployed the OpenShift Virtualization Operator
   - 5.1 Created the Virtualization instance (Enable VM creation)
8. Deployed the NMState Operator
   - 6.1 Created a NMState DNS configuration for the nodes (Due to long DNS search domain entries; limit 251 chars)
9. Deployed kube-burner

# Testing order

1. Node Failure/Reboot (k8s)
   - Graceful/Abrupt
3. K8s VM Scheduling distrobution
   - Max paths per host
4. API Server (iBox)
5. Iterate Batch (w/Active IO; Rescan impact)
6. CSI-Clone vs. Snapshot

# Helpful links
Some work pulled from:
https://hackmd.io/@johnsimcall/BkElnsvUA

FIO Cheat Sheet:
https://gist.github.com/githubfoam/a678cfc813c7ede6ca9ecb93e34edd8e

IOStat Cheat Sheet:
https://www.golinuxcloud.com/iostat-command-in-linux/
