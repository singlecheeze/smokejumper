https://www.ibm.com/docs/en/fusion-software/2.12.0?topic=san-planning-prerequisites  
  
A registry is required for operator deployment. To use internal registry:
```
[root@r730ocp5 core]# oc get -o jsonpath='{.spec}' configs.imageregistry.operator.openshift.io/cluster | jq '. | (.managementState, .storage)'
"Removed"
{}

[root@r730ocp5 core]# oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"managementState":"Managed"}}'
config.imageregistry.operator.openshift.io/cluster patched

[root@r730ocp5 core]# oc get pod -n openshift-image-registry -l docker-registry=default
No resources found in openshift-image-registry namespace.

[root@r730ocp5 core]# oc get clusteroperator image-registry
NAME             VERSION   AVAILABLE   PROGRESSING   DEGRADED   SINCE   MESSAGE
image-registry   4.20.3    False       True          True       18m     Available: The deployment does not have available replicas...
```
Create a Pull Secret:  
```
oc create secret -n ibm-fusion-access generic fusion-pullsecret --from-literal=ibm-entitlement-key=<Put Key Here>
```
  
For limiting cluster resource use: https://www.ibm.com/docs/en/scalecontainernative/5.2.3?topic=resources-cluster#roles  
Note: This didn't seem to lower the utilization post-apply
<img width="1593" height="674" alt="image" src="https://github.com/user-attachments/assets/277c80a1-a7c8-424b-bdf5-add9465ce066" />
```yaml
apiVersion: scale.spectrum.ibm.com/v1beta1
kind: Cluster
spec:
  ...
  daemon:
    roles:
    - name: client
      resources:
        cpu: "2"
        memory: 4Gi
      limits:
        cpu: "4"
        memory: 8Gi
```
