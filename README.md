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
7. Set "Max Pods"
8. Deployed the OpenShift Virtualization Operator
   - 5.1 Created the Virtualization instance (Enable VM creation)
9. Deployed the NMState Operator
   - 6.1 Created a NMState DNS configuration for the nodes (Due to long DNS search domain entries; limit 251 chars)
10. Deployed kube-burner

# Testing order

1. K8s VM Scheduling distribution
   - Max paths per host
2. Iterate Batch
   - w/Active IO
   - Rescan impact (Some sort of rescan delay?)
      - Need to batch the rescan "echo --- to host18/rescan" to insure rescans aren't issued in excess
   - How to hint to the CSI that it should map storage on the same node we are annotating the VM to be scheduled on
4. Node Failure/Reboot (k8s)
   - Graceful/Abrupt
5. API Server (iBox)
6. CSI-Clone vs. Snapshot

# Helpful links  
https://docs.oracle.com/en/operating-systems/oracle-linux/6/admin/query-udevandsysfs.html  

Some work pulled from:  
https://hackmd.io/@johnsimcall/BkElnsvUA  
https://access.redhat.com/solutions/7051974  
https://access.redhat.com/solutions/26017  
https://access.redhat.com/solutions/137073  

FIO Cheat Sheet:
https://gist.github.com/githubfoam/a678cfc813c7ede6ca9ecb93e34edd8e

IOStat Cheat Sheet:
https://www.golinuxcloud.com/iostat-command-in-linux/
