# Abreviated How To Install Guide for OpenShift (InfoScale 8.0.4)  
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
5. 
6. 
