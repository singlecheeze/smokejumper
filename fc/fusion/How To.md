### Installation  
https://www.ibm.com/docs/en/fusion-software/2.12.0?topic=san-planning-prerequisites  
  
#### A registry is required for operator deployment  
See: https://github.com/singlecheeze/smokejumper/blob/main/tips/helpful-commands.md  

#### Create a Pull Secret:  
```
oc create secret -n ibm-fusion-access generic fusion-pullsecret --from-literal=ibm-entitlement-key=<Put Key Here>
```

#### Setup Mulitpath for your LUNs:
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
#### Rescan:
```
rescan-scsi-bus.sh -f -r -a -m
```
#### Find LUNs and make sure multipath'd correctly:
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

#### Get Device UUIDs (In this case I'm using two drives from each node):
```
[root@r730ocp5 core]# udevadm info -q property -n /dev/dm-2 | grep WWN
DM_WWN=0x62000000de9068dd5df525300a2a0f49

[root@r730ocp5 core]# udevadm info -q property -n /dev/dm-0 | grep WWN
DM_WWN=0x62000000d9446f8a28835e060a2a0f49
```

#### Create FileSystemClaim:  
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
  
#### For limiting cluster resources:  
https://www.ibm.com/docs/en/scalecontainernative/5.2.3?topic=resources-cluster#roles   
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
### Administration:  
#### Deleting a FileSystem:
```
[root@r730ocp5 core]# oc label filesystem big-fat-lun -n ibm-spectrum-scale scale.spectrum.ibm.com/allowDelete=
filesystem.scale.spectrum.ibm.com/big-fat-lun labeled

[root@r730ocp5 core]# oc delete FileSystem big-fat-lun -n ibm-spectrum-scale
filesystem.scale.spectrum.ibm.com "big-fat-lun" deleted
```

### Performance:  
Hosts: 3x Dell R730xd, 48x Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz, 198 GB @2133 MHz, Emulex LightPulse LPe32002-M2 2-Port 32Gb FC HBA  
SAN: QuantaStor 6.6.5.026+4f21833dd6, GigaByte R272-Z34 2U24, AMD EPYC 7302P 16-Core Processor, 24x Intel DC P4510 SSDPE2KX010T8 in RAID10, ZFS Sync Policy Standard, LZ4 Compression  
  
<details>
    <summary>Win22K, No Virtio Custom, Fusion, Warm Cache</summary>

<img width="797" height="960" alt="Win22KNoVirtioCustomFusionWarmCache" src="https://github.com/user-attachments/assets/b5546bb6-0eb5-4d07-a6b5-0ebf8a98021c" />
  
</details>

<details>
    <summary>Win22K, No Virtio Custom, Fusion, Warm Cache, Two Drives</summary>

<img width="795" height="962" alt="Win22KNoVirtioCustomFusionWarmCacheTwoDrives" src="https://github.com/user-attachments/assets/7dd39ff9-5ec2-4f9d-b703-d07febf7a20d" />
  
</details>

<details>
    <summary>Win22K, Yes Virtio Custom, Fusion, Warm Cache</summary>

<img width="795" height="963" alt="Win22KYesVirtioCustomFusionWarmCache" src="https://github.com/user-attachments/assets/635921da-7bf4-4486-9676-932a0a145474" />
  
</details>
