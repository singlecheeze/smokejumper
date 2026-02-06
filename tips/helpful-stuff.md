#### VM Migrations:  
Install Migration Toolkit for Containers  
Note: If you get an error that a disk isn't migratable and it's been migrated in the past, check the labels on the DataVolume and delete the one concerning live migration as it's probably pointing to an old resource.

#### VM Disk Performance (VirtIO Disks):
VM disk performance may be sped up by adding additional worker storage threads withing the VirtIO storage subsystem in the VM YAML:  
Ref: https://developers.redhat.com/blog/2025/06/23/feature-introduction-multiple-iothreads-openshift-virtualization#overview  
```yaml
 spec:
    domain:
      cpu:
        cores: 1
        sockets: 16
        threads: 1
      memory:
        guest: 16Gi
      ioThreadsPolicy: supplementalPool
      ioThreads:
        supplementalPoolThreadCount: 4
      devices:
        blockMultiQueue: true
        disks:
        - name: rootdisk
          disk:
            bus: virtio
```
Specifically:
```
ioThreadsPolicy: supplementalPool
 ioThreads:
   supplementalPoolThreadCount: 4
 devices:
   blockMultiQueue: true
```

#### To use the internal registry:
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

[root@r730ocp5 core]# oc patch configs.imageregistry.operator.openshift.io/cluster --type merge -p '{"spec":{"defaultRoute":true}}'
config.imageregistry.operator.openshift.io/cluster patched

To configure storage (Deleted on reboot):
oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"storage":{"emptyDir":{}}}}'

OR persisted (Leave the claim field blank to allow the automatic creation of an image-registry-storage PVC of 100 GB)
oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"storage":{"pvc":{"claim":{}}}}}'
```

#### Manually clean up disk space on nodes:
Find Large Directories:
```
du -sh /var/lib/containers/storage/*
```
Removes stopped containers, unused images, networks, build cache:
```
podman system prune -f
```
Removes all unused images:
```
podman image prune -a -f
```
TRIM (Discard):
```
fstrim -av
```
Or do it all:
```
podman system prune -f && podman image prune -a -f && fstrim -av
```
