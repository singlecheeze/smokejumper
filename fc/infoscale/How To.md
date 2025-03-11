# Abreviated Install Guide for OpenShift (InfoScale 8.0.4)  
https://www.veritas.com/support/en_US/doc/168721626-168743109-1  
  
### Rrequired Operators (Do in this order)
1. Cert-manager v1.11 or later on OCP 4.12 or Cert-manager v1.7.1 on OCP 4.11 (Red Hat-certified) must be installed
2. Node Feature Discovery
3. InfoScale Licensing Operator
4. InfoScale SDS Operator
   1. During download and installation of operators, when prompted ensure that 8.0.400x is selected as the Update channel and All namespaces on the cluster is selected as the Installation mode as under.
   2. In the following screen, select the namespace where you want to install in Installed Namespace and Manual in Update approval. Click Install.
   3. Click Approve for Manual approval required.
   4. Wait till installation is complete. InfoScale Licensing Operator and Node Feature Discovery Operator along with InfoScale SDS operator are installed in the namespace you provide. Cert-manager, InfoScale Licensing Operator, and Node Feature Discovery Operator are the dependencies for InfoScale installation. If any of these dependencies are already installed in the namespace you provide or openshift-operators, installation is skipped. License must be applied before installing InfoScale.
5. In the left frame, select Operators > Installed Operators. Check if Status of all Operators is Succeeded as under.
6. Note: If NFD instance is already created, skip all steps related to Node Feature Discovery.
7. In Node Feature Discovery Operator, click Create NodeFeatureDiscovery in the upper-right corner of the screen.
8. After a successful creation of Node Feature Discovery, click Workloads > Pods in the left frame. Review names of the listed pods. Node Feature Discovery must be created on all nodes and is indicated by a prefix nfd.
9. You can now apply the license. Click Operators > Installed Operators in the left frame.
10. In the screen that opens, click Create License in the upper-right corner of your screen.
11.  In License Edition, select the type of license.
   1. Note: If you want to install and configure Disaster Recovery (DR), you must have Enterprise type of license.
12. Click Create to apply the license.
13. Click Create InfoScaleCluster in the upper-right corner of your screen. The following screen opens.
14. Choose a project to create InfoScale cluster. Enter Name, Namespace, and InfoScale ClusterID for the cluster. If you are installing in an airgapped environment, enter Image Registry for pulling images. To install on a system with Internet connectivity, do not enter any value for Image Registry.
   1. Note: If you do not enter InfoScale ClusterID, a ClusterID is randomly generated and assigned. The ClusterID is suffixed to the disk group.
15. Click InfoScale Cluster Information. Enter information about the nodes here. Enter Node name . Optionally, you can enter IP addresses of nodes in Node IPs and the device path of the disk that you want to exclude from the InfoScale disk group in Exclude-device list. You can also add fencing devices in Fencing device list. For each node, you must add two IP addresses.
  1. Note: OpenShift cluster must have at least two nodes as minimum two nodes are needed to form an InfoScale cluster.
16.
     


