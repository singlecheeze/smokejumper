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

Setup Mulitpath for your LUNs:
```
[root@r730ocp5 core]# cat /etc/multipath.conf
defaults {
    user_friendly_names         "yes"
    find_multipaths             "yes"
    uid_attribute               "ID_SERIAL" # This removes getuid_callout deprecation warning when using this below: (getuid_callout         "/lib/udev/scsi_id --whitelisted --replace-whitespace --device=/dev/%n")
}
blacklist {
    devnode                     "^nvme"
    # Blacklist all VXFS WWNs
    wwid "36200000075e7adaebf3e6ae80a2a0f49"
}
devices {
     device {
        vendor                 "OSNEXUS"
        product                "QUANTASTOR"
        #prio                   "alua"
        hardware_handler       "1 alua"
        path_grouping_policy   "group_by_prio"
        failback               "immediate"
        no_path_retry          10
        rr_min_io              1
        path_checker           "tur"
        rr_weight              "uniform"
   }
}
```
Rescan:
```
rescan-scsi-bus.sh -f -r -a -m
```
Find LUNs and make sure multipath'd correctly:
```
[root@r730ocp5 core]# multipath -ll
mpatha (362000000fa1ae7c3809efe6f0a2a0f49) dm-1 OSNEXUS,QUANTASTOR
size=120G features='1 queue_if_no_path' hwhandler='0' wp=rw
`-+- policy='service-time 0' prio=1 status=active
  |- 2:0:0:5  sdf 8:80  active ready running
  |- 2:0:1:5  sdc 8:32  active ready running
  |- 12:0:0:5 sdh 8:112 active ready running
  `- 12:0:1:5 sdk 8:160 active ready running
mpathc (362000000d9446f8a28835e060a2a0f49) dm-0 OSNEXUS,QUANTASTOR
size=931G features='1 queue_if_no_path' hwhandler='0' wp=rw
`-+- policy='service-time 0' prio=1 status=active
  |- 12:0:0:7 sdm 8:192 active ready running
  |- 12:0:1:7 sdo 8:224 active ready running
  |- 2:0:1:7  sdq 65:0  active ready running
  `- 2:0:0:7  sdi 8:128 active ready running
mpathd (362000000de9068dd5df525300a2a0f49) dm-2 OSNEXUS,QUANTASTOR
size=931G features='1 queue_if_no_path' hwhandler='0' wp=rw
`-+- policy='service-time 0' prio=1 status=active
  |- 12:0:0:8 sdn 8:208 active ready running
  |- 12:0:1:8 sdp 8:240 active ready running
  |- 2:0:1:8  sdr 65:16 active ready running
  `- 2:0:0:8  sdl 8:176 active ready running
```

Get Device UUIDs (In this case I'm using two drives from each node):
```
[root@r730ocp5 core]# udevadm info -q property -n /dev/dm-0
DEVPATH=/devices/virtual/block/dm-0
DEVNAME=/dev/dm-0
DEVTYPE=disk
DISKSEQ=93
MAJOR=253
MINOR=0
SUBSYSTEM=block
USEC_INITIALIZED=266653037230
DM_UDEV_DISABLE_LIBRARY_FALLBACK_FLAG=1
DM_UDEV_PRIMARY_SOURCE_FLAG=1
DM_SUBSYSTEM_UDEV_FLAG0=1
DM_ACTIVATION=0
DM_NAME=mpathc
DM_UUID=mpath-362000000d9446f8a28835e060a2a0f49
DM_SUSPENDED=0
DM_UDEV_RULES_VSN=2
MPATH_DEVICE_READY=1
MPATH_SBIN_PATH=/sbin
MPATH_UNCHANGED=1
DM_TYPE=scsi
DM_WWN=0x62000000d9446f8a28835e060a2a0f49
DM_SERIAL=362000000d9446f8a28835e060a2a0f49
NVME_HOST_IFACE=none
SYSTEMD_READY=1
DEVLINKS=/dev/disk/by-id/wwn-0x62000000d9446f8a28835e060a2a0f49 /dev/mapper/mpathc /dev/disk/by-id/dm-name-mpathc /dev/disk/by-id/scsi-362000000d9446f8a28835e060a2a0f49 /de>
TAGS=:systemd:
CURRENT_TAGS=:systemd:

[root@r730ocp5 core]# udevadm info -q property -n /dev/dm-2
DEVPATH=/devices/virtual/block/dm-2
DEVNAME=/dev/dm-2
DEVTYPE=disk
DISKSEQ=94
MAJOR=253
MINOR=2
SUBSYSTEM=block
USEC_INITIALIZED=266653064400
DM_UDEV_DISABLE_LIBRARY_FALLBACK_FLAG=1
DM_UDEV_PRIMARY_SOURCE_FLAG=1
DM_SUBSYSTEM_UDEV_FLAG0=1
DM_ACTIVATION=0
DM_NAME=mpathd
DM_UUID=mpath-362000000de9068dd5df525300a2a0f49
DM_SUSPENDED=0
DM_UDEV_RULES_VSN=2
MPATH_DEVICE_READY=1
MPATH_SBIN_PATH=/sbin
MPATH_UNCHANGED=1
DM_TYPE=scsi
DM_WWN=0x62000000de9068dd5df525300a2a0f49
DM_SERIAL=362000000de9068dd5df525300a2a0f49
NVME_HOST_IFACE=none
SYSTEMD_READY=1
DEVLINKS=/dev/disk/by-id/dm-name-mpathd /dev/disk/by-id/dm-uuid-mpath-362000000de9068dd5df525300a2a0f49 /dev/disk/by-id/wwn-0x62000000de9068dd5df525300a2a0f49 /dev/mapper/m>
TAGS=:systemd:
CURRENT_TAGS=:systemd:
```

Create FileSystemClaim:  
Note: One drive is fine or use two or more like in the YAML  
<img width="925" height="920" alt="image" src="https://github.com/user-attachments/assets/3980834d-9b5d-43e9-9bfd-99fcf3946da3" />
```
kind: FileSystemClaim
apiVersion: fusion.storage.openshift.io/v1alpha1
metadata:
  labels:
    app.kubernetes.io/managed-by: kustomize
    app.kubernetes.io/name: openshift-fusion-access-operator
  name: filesystemclaim-sample
  namespace: ibm-spectrum-scale
spec:
  devices:
    - '0x62000000de9068dd5df525300a2a0f49'
    - '0x62000000d9446f8a28835e060a2a0f49'
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

Deleting a FileSystem:
```
[root@r730ocp5 core]# oc label filesystem big-fat-lun -n ibm-spectrum-scale scale.spectrum.ibm.com/allowDelete=
filesystem.scale.spectrum.ibm.com/big-fat-lun labeled

[root@r730ocp5 core]# oc delete FileSystem big-fat-lun -n ibm-spectrum-scale
filesystem.scale.spectrum.ibm.com "big-fat-lun" deleted
```

VM Migrations:
Install Migration Toolkit for Containers
Note: If you get an error that a disk isn't migratable and it's been migrated in the past, check the labels on the DataVolume and delete the one concerning live migration as it's probably pointing to an old resource.
