# Abreviated Install Guide for OpenShift (InfoScale 8.0.4)  
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
        - '/dev/disk/by-path/pci-0000:82:00.0-fc-0x21000024ff1e85b6-lun-6'
      ip:
        - 172.16.1.113
      nodeName: r730ocp3.localdomain
    - includeDevices:
        - '/dev/disk/by-path/pci-0000:82:00.0-fc-0x21000024ff1e85b6-lun-6'
      ip:
        - 172.16.1.114
      nodeName: r730ocp4.localdomain
    - includeDevices:
        - '/dev/disk/by-path/pci-0000:82:00.0-fc-0x21000024ff1e85b6-lun-6'
      ip:
        - 172.16.1.115
      nodeName: r730ocp5.localdomain
  sameEncKey: false
  enableScsi3pr: false
  isSharedStorage: true
  version: 9.1.0
```
### Storage Profile
Note: You may need to go edit the storage profile that geta automatically created when you create a storage class
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
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-infoscale-sc
annotations:
  storageclass.kubernetes.io/is-default-class: "true"
provisioner: org.veritas.infoscale
reclaimPolicy: Delete
allowVolumeExpansion: true
parameters: fstype: vxfs
  layout: "stripe"
  nstripe: "1"
  stripeUnit: "64k"
  initType: "active"
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
