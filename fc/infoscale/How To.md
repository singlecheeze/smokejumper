# Abreviated Install Guide for OpenShift (InfoScale 9.0.1)  
https://www.veritas.com/support/en_US/doc/168721626-168743109-1  
  
### Required Operators (Do in this order)
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
11. In License Edition, select the type of license.
    1. Note: If you want to install and configure Disaster Recovery (DR), you must have Enterprise type of license.
12. Click Create to apply the license.
13. Click Create InfoScaleCluster in the upper-right corner of your screen. The following screen opens.
14. Choose a project to create InfoScale cluster. Enter Name, Namespace, and InfoScale ClusterID for the cluster. If you are installing in an airgapped environment, enter Image Registry for pulling images. To install on a system with Internet connectivity, do not enter any value for Image Registry.
    1. Note: If you do not enter InfoScale ClusterID, a ClusterID is randomly generated and assigned. The ClusterID is suffixed to the disk group.
15. Click InfoScale Cluster Information. Enter information about the nodes here. Enter Node name. Optionally, you can enter IP addresses of nodes in Node IPs and the device path of the disk that you want to exclude from the InfoScale disk group in Exclude-device list. You can also add fencing devices in Fencing device list. For each node, you must add two IP addresses.
    1. Note: OpenShift cluster must have at least two nodes as minimum two nodes are needed to form an InfoScale cluster.
16. Click Create to create an InfoScale cluster. Cluster formation begins. Watch the status message.
    1. It changes to "FencingConfigured"
    2. Then changes to "DgCreated"
    3. Finally "Running"
  
### License
```yaml
apiVersion: vlic.veritas.com/v1
kind: License
metadata:
  name: license-dev
spec:
  licenseEdition: "Developer"
```

### Cluster
```yaml
apiVersion: infoscale.veritas.com/v1
kind: InfoScaleCluster
metadata:
  name: infoscalecluster-dev
  namespace: infoscale-vtas
spec:
  encrypted: false
  clusterInfo:
    - includeDevices:
        - '/dev/disk/by-path/pci-0000:82:00.0-fc-0x21000024ff1e85b7-lun-2'
      nodeName: r730ocp3.localdomain
    - includeDevices:
        - '/dev/disk/by-path/pci-0000:82:00.0-fc-0x21000024ff1e85b7-lun-2'
      nodeName: r730ocp4.localdomain
    - includeDevices:
        - '/dev/disk/by-path/pci-0000:82:00.0-fc-0x21000024ff1e85b7-lun-2'
      nodeName: r730ocp5.localdomain
  sameEncKey: false
  enableScsi3pr: false
  isSharedStorage: true
  version: 9.1.0
```
### Storage Profile
Note: You may need to go edit the storage profile that geta automatically created when you create a storage class and add the proper claimPropertySets to the spec
```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: StorageProfile
metadata:
  name: csi-infoscale-sc
spec:
  claimPropertySets:
    - accessModes:
        - ReadWriteMany
      volumeMode: Block
    - accessModes:
        - ReadWriteOnce
      volumeMode: Block
    - accessModes:
        - ReadWriteOnce
      volumeMode: Filesystem
  cloneStrategy: csi-clone
status:
  cloneStrategy: csi-clone
  dataImportCronSourceFormat: pvc
  provisioner: org.veritas.infoscale
  snapshotClass: csi-infoscale-sc-snapclass
  storageClass: csi-infoscale-sc
```
### Storage Class
```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: csi-infoscale-sc
  annotations:
    storageclass.kubernetes.io/is-default-class: 'true'
provisioner: org.veritas.infoscale
parameters:
  fstype: vxfs
  initType: active
  layout: concat
reclaimPolicy: Delete
allowVolumeExpansion: true
```
### Monitoring
Create/Edit cluster-monitoring-config in the openshift-monitoring namespace as under.
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
data:
  config.yaml: |
    enableUserWorkload: true
```
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: infoscale-metrics
  namespace: infoscale-vtas
  labels:
    release: kube-prometheus
spec:
  selector:
    matchLabels:
      cvmmaster: "true"
  podMetricsEndpoints:
  - path: /infoscale/api/2.0/metrics
    port: rest-endpoint
    interval: 2m
    scrapeTimeout: 30s
    scheme: https
    tlsConfig:
      ca:
        secret:
          key: ca.crt
          name: infoscale-prom-tls
      cert:
        secret:
          key: tls.crt
          name: infoscale-prom-tls
      keySecret:
        key: tls.key
        name: infoscale-prom-tls
      serverName: infoscale-sds-rest-59131  # <Cluster ID>
```

### Appendix
For certain arrays (Like QuantaStor), InfoScale will need a profile that doesn't exist (Mainly driven by Arctera HCL), so one will need to be created.  
Ref: https://www.veritas.com/support/en_US/doc/79722584-159001485-0/v31177640-159001485  
Note: This currently does not persist past reboot of the node in infoscale-sds-operator.v9.1.0 but Arctera is working on it.  
Must run from SDS pods:
```
sh-5.1# vxddladm addjbod vid=OSNEXUS pid="QUANTASTOR" serialnum=18/080/4/0x14

sh-5.1# vxdisk list
DEVICE          TYPE            DISK         GROUP        STATUS
disk_0       auto:none       -            -            online invalid
disk_1       auto:cdsdisk    disk_0       vrts_kube_dg-4628 online clone_disk shared
disk_2       auto:none       -            -            online invalid

sh-5.1# vxddladm listjbod
VID      PID                SerialNum               CabinetNum        Policy
                      (Cmd/PageCode/off/len)  (Cmd/PageCode/off/len) 
==============================================================================
OSNEXUS  QUANTASTOR      18/-1/4/20                  -                Disk      

sh-5.1# vxdisk set disk_1 clone=off

sh-5.1# vxdisk list
DEVICE          TYPE            DISK         GROUP        STATUS
disk_0       auto:none       -            -            online invalid
disk_1       auto:cdsdisk    disk_0       vrts_kube_dg-4628 online shared
disk_2       auto:none       -            -            online invalid
```
`serialnum=18/080/4/0x14` is derived from:
```
sh-5.1# /etc/vx/diag.d/vxscsiinq -d /dev/vx/rdmp/disk_1

Inquiry for /dev/vx/rdmp/disk_1, evpd 0x0, page code 0x0
Peripheral Qualifier/Device Type : 0
Removable bit : 0
Device type modifier : 0
ISO Version : 0
ECMA Version : 0
ANSI Version : 6
AEN Capability : 0
Terminat I/O Capability : 0
Additional Length : 3f
Relative Addressing : 0
32 bit I/O : 0
16 bit I/O : 0
Sync capabilities : 0
Linked command : 0
Command Queing : 1
Soft Reset : 0
Vendor Identification : OSNEXUS 
Product Identification : QUANTASTOR      
Revision Number : 390 
Serial Number : 
        /dev/vx/rdmp/disk_1: Raw data size 68
Bytes:   0 -   7    0x00  0x00  0x06  0x22  0x3f  0x08  0x10  0x02  ..."?...
Bytes:   8 -  15    0x4f  0x53  0x4e  0x45  0x58  0x55  0x53  0x20  OSNEXUS 
Bytes:  16 -  23    0x51  0x55  0x41  0x4e  0x54  0x41  0x53  0x54  QUANTAST
Bytes:  24 -  31    0x4f  0x52  0x20  0x20  0x20  0x20  0x20  0x20  OR      
Bytes:  32 -  39    0x33  0x39  0x30  0x20  0x00  0x00  0x00  0x00  390 ....
Bytes:  40 -  47    0x00  0x00  0x00  0x00  0x00  0x00  0x00  0x00  ........
Bytes:  48 -  55    0x00  0x00  0x00  0x00  0x00  0x00  0x00  0x00  ........
Bytes:  56 -  63    0x00  0x00  0x00  0x8b  0x0d  0xa0  0x09  0x00  ........
Bytes:  64 -  67    0x04  0x63  0x04  0xc0                          .c..


sh-5.1# /etc/vx/diag.d/vxscsiinq -d -e 1 -p 0x80 /dev/vx/rdmp/disk_1

Inquiry for /dev/vx/rdmp/disk_1, evpd 0x1, page code 0x80
Peripheral Qualifier/Device Type : 0
Length of serial number          : 20
Product serial number            : 75e7adaebf3e6ae80a2a
        /dev/vx/rdmp/disk_1: Raw data size 24
Bytes:   0 -   7    0x00  0x80  0x00  0x14  0x37  0x35  0x65  0x37  ....75e7
Bytes:   8 -  15    0x61  0x64  0x61  0x65  0x62  0x66  0x33  0x65  adaebf3e
Bytes:  16 -  23    0x36  0x61  0x65  0x38  0x30  0x61  0x32  0x61  6ae80a2a


sh-5.1# /etc/vx/diag.d/vxscsiinq -d -e 1 -p 0x83 /dev/vx/rdmp/disk_1

Inquiry for /dev/vx/rdmp/disk_1, evpd 0x1, page code 0x83
------- Identifier Descriptor 1 -------
ID type             : 0x1 (T10 vendor ID based)
Protocol Identifier : 0x0
Code set            : 0x2
PIV                 : 0x0
Association         : 0x0
Length              : 0x21
Data                : OSNEXUS a2a0f49bdcea1aa-75e7adaeb
------- Identifier Descriptor 2 -------
ID type             : 0x4 (Relative target port)
Protocol Identifier : 0x0
Code set            : 0x1
PIV                 : 0x0
Association         : 0x1
Length              : 0x4
Data                : 000004bd
------- Identifier Descriptor 3 -------
ID type             : 0x3 (NAA)
Protocol Identifier : 0x0
Code set            : 0x1
PIV                 : 0x0
Association         : 0x0
Length              : 0x10
Data                : 6200000075e7adaebf3e6ae80a2a0f49
        /dev/vx/rdmp/disk_1: Raw data size 69
Bytes:   0 -   7    0x00  0x83  0x00  0x41  0x02  0x01  0x00  0x21  ...A...!
Bytes:   8 -  15    0x4f  0x53  0x4e  0x45  0x58  0x55  0x53  0x20  OSNEXUS 
Bytes:  16 -  23    0x61  0x32  0x61  0x30  0x66  0x34  0x39  0x62  a2a0f49b
Bytes:  24 -  31    0x64  0x63  0x65  0x61  0x31  0x61  0x61  0x2d  dcea1aa-
Bytes:  32 -  39    0x37  0x35  0x65  0x37  0x61  0x64  0x61  0x65  75e7adae
Bytes:  40 -  47    0x62  0x01  0x14  0x00  0x04  0x00  0x00  0x04  b.......
Bytes:  48 -  55    0xbd  0x01  0x03  0x00  0x10  0x62  0x00  0x00  .....b..
Bytes:  56 -  63    0x00  0x75  0xe7  0xad  0xae  0xbf  0x3e  0x6a  .u....>j
Bytes:  64 -  68    0xe8  0x0a  0x2a  0x0f  0x49                    ..*.I
```

>The vid=OSNEXUS parameter is derived from the Standard Inquiry page (page 0x00), where the output explicitly reports Vendor Identification : OSNEXUS. This value is also visible in the raw hex dump at bytes 8–15, confirming the vendor string used by the device.
>
>The optional pid="QUANTASTOR" parameter comes from the same Standard Inquiry page (page 0x00). The output shows Product Identification : QUANTASTOR, which is located in bytes 16–31 of the inquiry data. While this parameter is not strictly required, including it helps ensure the rule applies only to this specific product and not to other devices from the same vendor.
>
>The serialnum field follows the required format opcode/pagecode/offset/length. The opcode value 18 corresponds to the SCSI INQUIRY command (0x12 in hexadecimal), as defined in the procedure. 
>
>The pagecode 080 refers to VPD page 0x80, which is the Unit Serial Number page. This page was queried using vxscsiinq -d -e 1 -p 0x80, and the output confirms that page 0x80 is supported and returns a valid serial number.
>
>The offset value 4 indicates the starting byte of the actual serial number within the page 0x80 response. In the raw hex dump, bytes 0–3 represent the page header (00 80 00 14), and the serial string begins at byte 4, where the ASCII characters of the serial number are stored.
>
>The length value 0x14 represents the size of the serial number in bytes. The output explicitly states Length of serial number : 20, which corresponds to hexadecimal value 0x14. This is also confirmed by the length field in bytes 2–3 of the page 0x80 header. 
>
>Together, these fields uniquely identify the disk using a stable and device-provided serial number, allowing Veritas DMP to correctly recognize and manage the device as a JBOD.
>

Helpful Commands from an SDS Pod (infoscale-sds-59131-1eb7816cdb4bd7f3-2grq4)
```
sh-5.1# vxdisk list
DEVICE          TYPE            DISK         GROUP        STATUS
disk_0       auto:cdsdisk    disk_0       vrts_kube_dg-59131 online shared


sh-5.1# vxdisk list disk_0
Device:    disk_0
devicetag: disk_0
type:      auto
clusterid: infoscale_59131
disk:      name=disk_0 id=1741211309.8.r730ocp3.localdomain
group:     name=vrts_kube_dg-59131 id=1741211310.10.r730ocp3.localdomain
info:      format=cdsdisk,privoffset=208,pubslice=3,privslice=3
flags:     online ready private autoconfig shared autoimport imported
pubpaths:  block=/dev/vx/dmp/disk_0s3 char=/dev/vx/rdmp/disk_0s3
guid:      {937900a6-fa0b-11ef-a49b-7ebb49213740}
udid:      OSNEXUS%5FQUANTASTOR%5FDISKS%5F62000000C6DA4107FD790678B5790928
site:      -
version:   4.1
iosize:    min=512 (bytes) max=128 (blocks)
public:    slice=3 offset=65744 len=2147417808 disk_offset=48
private:   slice=3 offset=208 len=65536 disk_offset=48
update:    time=1741633149 seqno=0.15
ssb:       actual_seqno=0.0
headers:   0 240
configs:   count=1 len=51360
logs:      count=1 len=4096
Defined regions:
 config   priv 000048-000239[000192]: copy=01 offset=000000 enabled
 config   priv 000256-051423[051168]: copy=01 offset=000192 enabled
 log      priv 051424-055519[004096]: copy=01 offset=000000 enabled
 lockrgn  priv 055520-055663[000144]: part=00 offset=000000
Multipathing information:
numpaths:   4
sdg             state=enabled
sdh             state=enabled
sde             state=enabled
sdf             state=enabled
connectivity: r730ocp5.localdomain r730ocp4.localdomain r730ocp3.localdomain


sh-5.1# cat /etc/llttab
set-node r730ocp5.localdomain
set-cluster 23411
link link0 udp - udp 50000 - 172.16.1.115 -
set-addr 0 link0 172.16.1.113
set-addr 1 link0 172.16.1.114
set-bcasthb 0
set-arp 0
set-discpeer 1
set-timer peerinact:1600


sh-5.1# vxprint -v
Disk group: vrts_kube_dg-59131
TY NAME         ASSOC        KSTATE   LENGTH   PLOFFS   STATE    TUTIL0  PUTIL0
v  vol_c51h5spa1dkn01c4076c fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_c51h5spa1dkn01c4076c_dcl gen ENABLED 67968 -     ACTIVE   -       -
v  vol_fjv8578nvs33n888c9w6 fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_fjv8578nvs33n888c9w6_dcl gen ENABLED 67968 -     ACTIVE   -       -
v  vol_kw15my7o47h1952n1hzg fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_kw15my7o47h1952n1hzg_dcl gen ENABLED 67968 -     ACTIVE   -       -
v  vol_wj689fdb31svj9q2m6lb fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_wj689fdb31svj9q2m6lb_dcl gen ENABLED 67968 -     ACTIVE   -       -
v  vol_6m3v2i516rw0h5h86327 fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_6m3v2i516rw0h5h86327_dcl gen ENABLED 67968 -     ACTIVE   -       -
v  vol_7vi69np2iiusz04wfh4v fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_7vi69np2iiusz04wfh4v_dcl gen ENABLED 67968 -     ACTIVE   -       -
v  vol_41t7e8pv9gs3863639o0 fsgen ENABLED 125829120 -   ACTIVE   -       -
v  vol_41t7e8pv9gs3863639o0_dcl gen ENABLED 70400 -     ACTIVE   -       -
v  vol_47dm6wm516ytm54qo1mo fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_47dm6wm516ytm54qo1mo_dcl gen ENABLED 67968 -     ACTIVE   -       -
v  vol_51mloyfrg7qq2y1qu33r fsgen ENABLED 20971520 -    ACTIVE   -       -
v  vol_51mloyfrg7qq2y1qu33r_dcl gen ENABLED 67840 -     ACTIVE   -       -
v  vol_74ms3x96f11k13j14d5c fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_74ms3x96f11k13j14d5c_dcl gen ENABLED 67968 -     ACTIVE   -       -
v  vol_88imh5e460h6664m56d7 fsgen ENABLED 125829120 -   ACTIVE   -       -
v  vol_88imh5e460h6664m56d7_dcl gen ENABLED 70400 -     ACTIVE   -       -
v  vol_604zv2ow6f3ci9o29a26 fsgen ENABLED 62914560 -    ACTIVE   -       -
v  vol_604zv2ow6f3ci9o29a26_dcl gen ENABLED 67968 -     ACTIVE   -       -


sh-5.1# vxprint -hdr
Disk group: vrts_kube_dg-59131

TY NAME         ASSOC        KSTATE   LENGTH   PLOFFS   STATE    TUTIL0  PUTIL0
dm disk_0       disk_0       -        2147417808 -      -        -       -


sh-5.1# vxprint -hdd
Disk group: vrts_kube_dg-59131

TY NAME         ASSOC        KSTATE   LENGTH   PLOFFS   STATE    TUTIL0  PUTIL0
dm disk_0       disk_0       -        2147417808 -      -        -       -


sh-5.1# vxprint -htr
Disk group: vrts_kube_dg-59131

DG NAME         NCONFIG      NLOG     MINORS   GROUP-ID
ST NAME         STATE        DM_CNT   SPARE_CNT         APPVOL_CNT
DM NAME         DEVICE       TYPE     PRIVLEN  PUBLEN   STATE
RV NAME         RLINK_CNT    KSTATE   STATE    PRIMARY  DATAVOLS  SRL
RL NAME         RVG          KSTATE   STATE    REM_HOST REM_DG    REM_RLNK
CO NAME         CACHEVOL     KSTATE   STATE
VT NAME         RVG          KSTATE   STATE    NVOLUME
V  NAME         RVG/VSET/CO  KSTATE   STATE    LENGTH   READPOL   PREFPLEX UTYPE
PL NAME         VOLUME       KSTATE   STATE    LENGTH   LAYOUT    NCOL/WID MODE
SD NAME         PLEX         DISK     DISKOFFS LENGTH   [COL/]OFF DEVICE   MODE
SV NAME         PLEX         VOLNAME  NVOLLAYR LENGTH   [COL/]OFF AM/NM    MODE
SC NAME         PLEX         CACHE    DISKOFFS LENGTH   [COL/]OFF DEVICE   MODE
DC NAME         PARENTVOL    LOGVOL
SP NAME         SNAPVOL      DCO
EX NAME         ASSOC        VC                       PERMS    MODE     STATE
SR NAME         KSTATE

dg vrts_kube_dg-59131 default default 55000    1741211310.10.r730ocp3.localdomain

dm disk_0       disk_0       auto     65536    2147417808 -

v  vol_c51h5spa1dkn01c4076c - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_c51h5spa1dkn01c4076c-01 vol_c51h5spa1dkn01c4076c ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-13    vol_c51h5spa1dkn01c4076c-01 disk_0 377895168 62914560 0 disk_0 ENA
dc vol_c51h5spa1dkn01c4076c_dco vol_c51h5spa1dkn01c4076c vol_c51h5spa1dkn01c4076c_dcl
v  vol_c51h5spa1dkn01c4076c_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_c51h5spa1dkn01c4076c_dcl-01 vol_c51h5spa1dkn01c4076c_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-14    vol_c51h5spa1dkn01c4076c_dcl-01 disk_0 440809728 67968 0 disk_0 ENA

v  vol_fjv8578nvs33n888c9w6 - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_fjv8578nvs33n888c9w6-01 vol_fjv8578nvs33n888c9w6 ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-11    vol_fjv8578nvs33n888c9w6-01 disk_0 314912640 62914560 0 disk_0 ENA
dc vol_fjv8578nvs33n888c9w6_dco vol_fjv8578nvs33n888c9w6 vol_fjv8578nvs33n888c9w6_dcl
v  vol_fjv8578nvs33n888c9w6_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_fjv8578nvs33n888c9w6_dcl-01 vol_fjv8578nvs33n888c9w6_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-12    vol_fjv8578nvs33n888c9w6_dcl-01 disk_0 377827200 67968 0 disk_0 ENA

v  vol_kw15my7o47h1952n1hzg - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_kw15my7o47h1952n1hzg-01 vol_kw15my7o47h1952n1hzg ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-21    vol_kw15my7o47h1952n1hzg-01 disk_0 696197760 62914560 0 disk_0 ENA
dc vol_kw15my7o47h1952n1hzg_dco vol_kw15my7o47h1952n1hzg vol_kw15my7o47h1952n1hzg_dcl
v  vol_kw15my7o47h1952n1hzg_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_kw15my7o47h1952n1hzg_dcl-01 vol_kw15my7o47h1952n1hzg_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-22    vol_kw15my7o47h1952n1hzg_dcl-01 disk_0 43505664 67968 0 disk_0 ENA

v  vol_wj689fdb31svj9q2m6lb - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_wj689fdb31svj9q2m6lb-01 vol_wj689fdb31svj9q2m6lb ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-19    vol_wj689fdb31svj9q2m6lb-01 disk_0 629621376 62914560 0 disk_0 ENA
dc vol_wj689fdb31svj9q2m6lb_dco vol_wj689fdb31svj9q2m6lb vol_wj689fdb31svj9q2m6lb_dcl
v  vol_wj689fdb31svj9q2m6lb_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_wj689fdb31svj9q2m6lb_dcl-01 vol_wj689fdb31svj9q2m6lb_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-20    vol_wj689fdb31svj9q2m6lb_dcl-01 disk_0 43437696 67968 0 disk_0 ENA

v  vol_6m3v2i516rw0h5h86327 - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_6m3v2i516rw0h5h86327-01 vol_6m3v2i516rw0h5h86327 ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-07    vol_6m3v2i516rw0h5h86327-01 disk_0 188947584 62914560 0 disk_0 ENA
dc vol_6m3v2i516rw0h5h86327_dco vol_6m3v2i516rw0h5h86327 vol_6m3v2i516rw0h5h86327_dcl
v  vol_6m3v2i516rw0h5h86327_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_6m3v2i516rw0h5h86327_dcl-01 vol_6m3v2i516rw0h5h86327_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-08    vol_6m3v2i516rw0h5h86327_dcl-01 disk_0 251862144 67968 0 disk_0 ENA

v  vol_7vi69np2iiusz04wfh4v - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_7vi69np2iiusz04wfh4v-01 vol_7vi69np2iiusz04wfh4v ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-09    vol_7vi69np2iiusz04wfh4v-01 disk_0 251930112 62914560 0 disk_0 ENA
dc vol_7vi69np2iiusz04wfh4v_dco vol_7vi69np2iiusz04wfh4v vol_7vi69np2iiusz04wfh4v_dcl
v  vol_7vi69np2iiusz04wfh4v_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_7vi69np2iiusz04wfh4v_dcl-01 vol_7vi69np2iiusz04wfh4v_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-10    vol_7vi69np2iiusz04wfh4v_dcl-01 disk_0 314844672 67968 0 disk_0 ENA

v  vol_41t7e8pv9gs3863639o0 - ENABLED ACTIVE   125829120 SELECT   -        fsgen
pl vol_41t7e8pv9gs3863639o0-01 vol_41t7e8pv9gs3863639o0 ENABLED ACTIVE 125829120 CONCAT - RW
sd disk_0-23    vol_41t7e8pv9gs3863639o0-01 disk_0 759112320 125829120 0 disk_0 ENA
dc vol_41t7e8pv9gs3863639o0_dco vol_41t7e8pv9gs3863639o0 vol_41t7e8pv9gs3863639o0_dcl
v  vol_41t7e8pv9gs3863639o0_dcl - ENABLED ACTIVE 70400  SELECT    -        gen
pl vol_41t7e8pv9gs3863639o0_dcl-01 vol_41t7e8pv9gs3863639o0_dcl ENABLED ACTIVE 70400 CONCAT - RW
sd disk_0-24    vol_41t7e8pv9gs3863639o0_dcl-01 disk_0 43573632 70400 0 disk_0 ENA

v  vol_47dm6wm516ytm54qo1mo - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_47dm6wm516ytm54qo1mo-01 vol_47dm6wm516ytm54qo1mo ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-05    vol_47dm6wm516ytm54qo1mo-01 disk_0 125965056 62914560 0 disk_0 ENA
dc vol_47dm6wm516ytm54qo1mo_dco vol_47dm6wm516ytm54qo1mo vol_47dm6wm516ytm54qo1mo_dcl
v  vol_47dm6wm516ytm54qo1mo_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_47dm6wm516ytm54qo1mo_dcl-01 vol_47dm6wm516ytm54qo1mo_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-06    vol_47dm6wm516ytm54qo1mo_dcl-01 disk_0 188879616 67968 0 disk_0 ENA

v  vol_51mloyfrg7qq2y1qu33r - ENABLED ACTIVE   20971520 SELECT    -        fsgen
pl vol_51mloyfrg7qq2y1qu33r-01 vol_51mloyfrg7qq2y1qu33r ENABLED ACTIVE 20971520 CONCAT - RW
sd disk_0-15    vol_51mloyfrg7qq2y1qu33r-01 disk_0 22259968 20971520 0 disk_0 ENA
dc vol_51mloyfrg7qq2y1qu33r_dco vol_51mloyfrg7qq2y1qu33r vol_51mloyfrg7qq2y1qu33r_dcl
v  vol_51mloyfrg7qq2y1qu33r_dcl - ENABLED ACTIVE 67840  SELECT    -        gen
pl vol_51mloyfrg7qq2y1qu33r_dcl-01 vol_51mloyfrg7qq2y1qu33r_dcl ENABLED ACTIVE 67840 CONCAT - RW
sd disk_0-16    vol_51mloyfrg7qq2y1qu33r_dcl-01 disk_0 43231488 67840 0 disk_0 ENA

v  vol_74ms3x96f11k13j14d5c - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_74ms3x96f11k13j14d5c-01 vol_74ms3x96f11k13j14d5c ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-01    vol_74ms3x96f11k13j14d5c-01 disk_0 566706816 62914560 0 disk_0 ENA
dc vol_74ms3x96f11k13j14d5c_dco vol_74ms3x96f11k13j14d5c vol_74ms3x96f11k13j14d5c_dcl
v  vol_74ms3x96f11k13j14d5c_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_74ms3x96f11k13j14d5c_dcl-01 vol_74ms3x96f11k13j14d5c_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-02    vol_74ms3x96f11k13j14d5c_dcl-01 disk_0 43369728 67968 0 disk_0 ENA

v  vol_88imh5e460h6664m56d7 - ENABLED ACTIVE   125829120 SELECT   -        fsgen
pl vol_88imh5e460h6664m56d7-01 vol_88imh5e460h6664m56d7 ENABLED ACTIVE 125829120 CONCAT - RW
sd disk_0-17    vol_88imh5e460h6664m56d7-01 disk_0 440877696 125829120 0 disk_0 ENA
dc vol_88imh5e460h6664m56d7_dco vol_88imh5e460h6664m56d7 vol_88imh5e460h6664m56d7_dcl
v  vol_88imh5e460h6664m56d7_dcl - ENABLED ACTIVE 70400  SELECT    -        gen
pl vol_88imh5e460h6664m56d7_dcl-01 vol_88imh5e460h6664m56d7_dcl ENABLED ACTIVE 70400 CONCAT - RW
sd disk_0-18    vol_88imh5e460h6664m56d7_dcl-01 disk_0 43299328 70400 0 disk_0 ENA

v  vol_604zv2ow6f3ci9o29a26 - ENABLED ACTIVE   62914560 SELECT    -        fsgen
pl vol_604zv2ow6f3ci9o29a26-01 vol_604zv2ow6f3ci9o29a26 ENABLED ACTIVE 62914560 CONCAT - RW
sd disk_0-03    vol_604zv2ow6f3ci9o29a26-01 disk_0 62982528 62914560 0 disk_0 ENA
dc vol_604zv2ow6f3ci9o29a26_dco vol_604zv2ow6f3ci9o29a26 vol_604zv2ow6f3ci9o29a26_dcl
v  vol_604zv2ow6f3ci9o29a26_dcl - ENABLED ACTIVE 67968  SELECT    -        gen
pl vol_604zv2ow6f3ci9o29a26_dcl-01 vol_604zv2ow6f3ci9o29a26_dcl ENABLED ACTIVE 67968 CONCAT - RW
sd disk_0-04    vol_604zv2ow6f3ci9o29a26_dcl-01 disk_0 125897088 67968 0 disk_0 ENA
```
