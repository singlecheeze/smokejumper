*General Links:*  
https://ubuntu.com/server/docs/common-multipath-tasks-and-procedures  

*Helpful Script:*  
```
./usr/bin/rescan-scsi-bus.sh
```
```
Scanning SCSI subsystem for new devices
Scanning host 0 for  SCSI target IDs 0 1 2 3 4 5 6 7, all LUNs
 Scanning for device 0 0 0 0 ...           
OLD: Host: scsi0 Channel: 00 Id: 00 Lun: 00
      Vendor: iDRAC    Model: Virtual CD       Rev: 0329
      Type:   CD-ROM                           ANSI SCSI revision: -1
 Scanning for device 0 0 0 1 ... 
OLD: Host: scsi0 Channel: 00 Id: 00 Lun: 01
      Vendor: iDRAC    Model: Virtual Floppy   Rev: 0329
      Type:   Direct-Access                    ANSI SCSI revision: -1
...............................Scanning host 1 for  SCSI target IDs 0 1 2 3 4 5 6 7, all LUNs
 Scanning for device 1 0 2 0 ... 
OLD: Host: scsi1 Channel: 00 Id: 02 Lun: 00
      Vendor: SEAGATE  Model: ST8000NM0075     Rev: PS26
      Type:   Direct-Access                    ANSI SCSI revision: 06
 Scanning for device 1 0 0 0 ... 
OLD: Host: scsi1 Channel: 00 Id: 00 Lun: 00
      Vendor: SEAGATE  Model: ST8000NM0075     Rev: PS26
      Type:   Direct-Access                    ANSI SCSI revision: 06
 Scanning for device 1 2 0 0 ... 
OLD: Host: scsi1 Channel: 02 Id: 00 Lun: 00
      Vendor: DELL     Model: PERC H730 Mini   Rev: 4.30
      Type:   Direct-Access                    ANSI SCSI revision: 05
 Scanning for device 1 0 1 0 ... 
OLD: Host: scsi1 Channel: 00 Id: 01 Lun: 00
      Vendor: SEAGATE  Model: ST8000NM0075     Rev: PS26
      Type:   Direct-Access                    ANSI SCSI revision: 06
Scanning host 2 for  all SCSI target IDs, all LUNs
 Scanning for device 2 0 1 2 ...           
OLD: Host: scsi2 Channel: 00 Id: 01 Lun: 02
      Vendor: OSNEXUS  Model: QUANTASTOR       Rev: 380 
      Type:   Direct-Access                    ANSI SCSI revision: 06
 Scanning for device 2 0 0 2 ...           
OLD: Host: scsi2 Channel: 00 Id: 00 Lun: 02
      Vendor: OSNEXUS  Model: QUANTASTOR       Rev: 380 
      Type:   Direct-Access                    ANSI SCSI revision: 06
Scanning host 3 for  all SCSI target IDs, all LUNs
 Scanning for device 3 0 1 2 ...           
OLD: Host: scsi3 Channel: 00 Id: 01 Lun: 02
      Vendor: OSNEXUS  Model: QUANTASTOR       Rev: 380 
      Type:   Direct-Access                    ANSI SCSI revision: 06
 Scanning for device 3 0 0 2 ...           
OLD: Host: scsi3 Channel: 00 Id: 00 Lun: 02
      Vendor: OSNEXUS  Model: QUANTASTOR       Rev: 380 
      Type:   Direct-Access                    ANSI SCSI revision: 06
0 new or changed device(s) found.          
0 remapped or resized device(s) found.
0 device(s) removed. 
```  

*Check Local Config:*  
```
# multipathd -k
multipathd> show config local
defaults {
        verbosity 2
        polling_interval 5
        max_polling_interval 20
        reassign_maps "no"
        multipath_dir "/lib64/multipath"
        path_selector "service-time 0"
        path_grouping_policy "failover"
        uid_attribute "ID_SERIAL"
        prio "const"
        prio_args ""
        features "0"
        path_checker "tur"
        alias_prefix "mpath"
        failback "manual"
        rr_min_io 1000
        rr_min_io_rq 1
        max_fds "max"
        rr_weight "uniform"
        queue_without_daemon "no"
        allow_usb_devices "no"
        flush_on_last_del "no"
        user_friendly_names "yes"
        fast_io_fail_tmo 5
        bindings_file "/etc/multipath/bindings"
        wwids_file "/etc/multipath/wwids"
        prkeys_file "/etc/multipath/prkeys"
        log_checker_err "always"
        all_tg_pt "no"
        retain_attached_hw_handler "yes"
        detect_prio "yes"
        detect_checker "yes"
        force_sync "no"
        strict_timing "no"
        deferred_remove "no"
        config_dir "/etc/multipath/conf.d"
        delay_watch_checks "no"
        delay_wait_checks "no"
        san_path_err_threshold "no"
        san_path_err_forget_rate "no"
        san_path_err_recovery_time "no"
        marginal_path_err_sample_time "no"
        marginal_path_err_rate_threshold "no"
        marginal_path_err_recheck_gap_time "no"
        marginal_path_double_failed_time "no"
        find_multipaths "on"
        uxsock_timeout 4000
        retrigger_tries 3
        retrigger_delay 10
        missing_uev_wait_timeout 30
        skip_kpartx "no"
        disable_changed_wwids "ignored"
        remove_retries 0
        ghost_delay "no"
        auto_resize "never"
        find_multipaths_timeout -10
        enable_foreign "NONE"
        marginal_pathgroups "off"
        recheck_wwid "no"
}
```

*Check File Descriptors:*  
https://access.redhat.com/solutions/3450832  
Multipath should have at least 2 FDs per path.
```
ls -l /proc/$(cat /var/run/multipathd.pid)/fd | wc -l
```
Modern multipath will: "By removing max_fds from /etc/multipath.conf the default value 'max' will now be used, equivalent to the systemwide value in /proc/sys/fs/nr_open, which itself is calculated as 1024 * 1024 = 1048576 (as of Red Hat Enterprise Linux 6.3). This should be more than enough for most systems."
```
cat /proc/sys/fs/nr_open
```

*Force Devmap Reload:*  
https://git.kernel.org/pub/scm/linux/storage/multipath/hare/multipath-tools.git/commit/?id=a4d0b34e841aae7e0722ba532ca46ff78b0f106e  
```
multipath -r dm-0
```
*Force Rescan:*  
https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/storage_administration_guide/scanning-storage-interconnects#scanning-storage-interconnects  
https://access.redhat.com/solutions/3941  
https://access.redhat.com/solutions/320883  
```
echo "c t l" >  /sys/class/scsi_host/hostH/scan
```
For example:
```
echo "- - 2" >  /sys/class/scsi_host/host3/scan
```
You can determine the H,c,t by referring to another device that is already configured on the same path as the new device. This can be done with commands such as lsscsi, scsi_id, multipath -l, and ls -l /dev/disk/by-*. This information, plus the LUN number of the new device, can be used as shown above to probe and configure that path to the new device.  

*Show paths and when they will be checked next:*  
```
multipathd -k
```
```
multipathd> show paths
hcil    dev     dev_t pri dm_st  chk_st dev_st  next_check     
1:0:0:0 sdb     8:16  1   undef  undef  unknown orphan         
1:0:1:0 sdc     8:32  1   undef  undef  unknown orphan         
1:0:2:0 sda     8:0   1   undef  undef  unknown orphan         
1:2:0:0 sdd     8:48  1   undef  undef  unknown orphan         
2:0:0:2 sdf     8:80  1   active ready  running XXXX...... 8/20
2:0:1:2 sdg     8:96  1   active ready  running XXX....... 7/20
3:0:0:2 sdh     8:112 1   active ready  running XXXX...... 8/20
3:0:1:2 sdi     8:128 1   active ready  running XXX....... 7/20
0:0:1:1 nvme0n1 259:0 1   undef  undef  unknown orphan  
```
*Query all udev attributes:*  
```
udevadm info --query=all --name=/dev/dm-0
```
```
P: /devices/virtual/block/dm-0
M: dm-0
R: 0
U: block
T: disk
D: b 253:0
N: dm-0
L: 50
S: disk/by-id/dm-name-mpatha
S: disk/by-id/wwn-0x620000007355abb3b8950167b5790928
S: disk/by-id/scsi-3620000007355abb3b8950167b5790928
S: mapper/mpatha
S: disk/by-id/dm-uuid-mpath-3620000007355abb3b8950167b5790928
Q: 17
E: DEVPATH=/devices/virtual/block/dm-0
E: DEVNAME=/dev/dm-0
E: DEVTYPE=disk
E: DISKSEQ=17
E: MAJOR=253
E: MINOR=0
E: SUBSYSTEM=block
E: USEC_INITIALIZED=40187700891
E: DM_UDEV_DISABLE_LIBRARY_FALLBACK_FLAG=1
E: DM_UDEV_PRIMARY_SOURCE_FLAG=1
E: DM_ACTIVATION=1
E: DM_NAME=mpatha
E: DM_UUID=mpath-3620000007355abb3b8950167b5790928
E: DM_SUSPENDED=0
E: DM_UDEV_RULES_VSN=2
E: MPATH_SBIN_PATH=/sbin
E: MPATH_DEVICE_READY=1
E: DM_TYPE=scsi
E: DM_WWN=0x620000007355abb3b8950167b5790928
E: DM_SERIAL=3620000007355abb3b8950167b5790928
E: NVME_HOST_IFACE=none
E: SYSTEMD_READY=1
E: DEVLINKS=/dev/disk/by-id/dm-name-mpatha /dev/disk/by-id/wwn-0x620000007355abb3b8950167b5790928 /dev/disk/by-id/scsi-3620000007355abb3b8950167b5790928 /dev/mapper/mpatha >
E: TAGS=:systemd:
E: CURRENT_TAGS=:systemd:
```
*Walk a device:*  
```
udevadm info --attribute-walk --name=/dev/sdg 
```
```
Udevadm info starts with the device specified by the devpath and then
walks up the chain of parent devices. It prints for every device
found, all possible attributes in the udev rules key format.
A rule to match, can be composed by the attributes of the device
and the attributes from one single parent device.

  looking at device '/devices/pci0000:80/0000:80:02.0/0000:82:00.0/host3/rport-3:0-4/target3:0:0/3:0:0:2/block/sdg':
    KERNEL=="sdg"
    SUBSYSTEM=="block"
    DRIVER==""
    ATTR{alignment_offset}=="0"
    ATTR{capability}=="0"
    ATTR{discard_alignment}=="0"
    ATTR{diskseq}=="12"
    ATTR{events}==""
    ATTR{events_async}==""
    ATTR{events_poll_msecs}=="-1"
    ATTR{ext_range}=="256"
    ATTR{hidden}=="0"
    ATTR{inflight}=="       0        0"
    ATTR{integrity/device_is_integrity_capable}=="0"
    ATTR{integrity/format}=="none"
    ATTR{integrity/protection_interval_bytes}=="0"
    ATTR{integrity/read_verify}=="0"
    ATTR{integrity/tag_size}=="0"
    ATTR{integrity/write_generate}=="0"
    ATTR{mq/0/cpu_list}=="1, 3, 5, 7, 9, 11, 25, 27, 29, 31, 33, 35"
    ATTR{mq/0/nr_reserved_tags}=="0"
    ATTR{mq/0/nr_tags}=="5884"
    ATTR{mq/1/cpu_list}=="13, 15, 17, 19, 21, 23, 37, 39, 41, 43, 45, 47"
    ATTR{mq/1/nr_reserved_tags}=="0"
    ATTR{mq/1/nr_tags}=="5884"
    ATTR{mq/2/cpu_list}=="0, 2, 4, 6, 8, 10, 24, 26, 28, 30, 32, 34"
    ATTR{mq/2/nr_reserved_tags}=="0"
    ATTR{mq/2/nr_tags}=="5884"
    ATTR{mq/3/cpu_list}=="12, 14, 16, 18, 20, 22, 36, 38, 40, 42, 44, 46"
    ATTR{mq/3/nr_reserved_tags}=="0"
    ATTR{mq/3/nr_tags}=="5884"
    ATTR{power/control}=="auto"
    ATTR{power/runtime_active_time}=="0"
    ATTR{power/runtime_status}=="unsupported"
    ATTR{power/runtime_suspended_time}=="0"
    ATTR{queue/add_random}=="0"
    ATTR{queue/chunk_sectors}=="0"
    ATTR{queue/dax}=="0"
    ATTR{queue/discard_granularity}=="65536"
    ATTR{queue/discard_max_bytes}=="1073741824"
    ATTR{queue/discard_max_hw_bytes}=="1073741824"
    ATTR{queue/discard_zeroes_data}=="0"
    ATTR{queue/dma_alignment}=="3"
    ATTR{queue/fua}=="1"
    ATTR{queue/hw_sector_size}=="512"
    ATTR{queue/io_poll}=="0"
    ATTR{queue/io_poll_delay}=="-1"
    ATTR{queue/io_timeout}=="30000"
    ATTR{queue/iostats}=="1"
    ATTR{queue/logical_block_size}=="512"
    ATTR{queue/max_discard_segments}=="1"
    ATTR{queue/max_hw_sectors_kb}=="2147483647"
    ATTR{queue/max_integrity_segments}=="0"
    ATTR{queue/max_sectors_kb}=="64"
    ATTR{queue/max_segment_size}=="65536"
    ATTR{queue/max_segments}=="256"
    ATTR{queue/minimum_io_size}=="65536"
    ATTR{queue/nomerges}=="0"
    ATTR{queue/nr_requests}=="5884"
    ATTR{queue/nr_zones}=="0"
    ATTR{queue/optimal_io_size}=="65536"
    ATTR{queue/physical_block_size}=="65536"
    ATTR{queue/read_ahead_kb}=="4096"
    ATTR{queue/rotational}=="0"
    ATTR{queue/rq_affinity}=="1"
    ATTR{queue/scheduler}=="[none] mq-deadline kyber bfq "
    ATTR{queue/stable_writes}=="0"
    ATTR{queue/virt_boundary_mask}=="0"
    ATTR{queue/wbt_lat_usec}=="2000"
    ATTR{queue/write_cache}=="write back"
    ATTR{queue/write_same_max_bytes}=="0"
    ATTR{queue/write_zeroes_max_bytes}=="268435456"
    ATTR{queue/zone_append_max_bytes}=="0"
    ATTR{queue/zone_write_granularity}=="0"
    ATTR{queue/zoned}=="none"
    ATTR{range}=="16"
    ATTR{removable}=="0"
    ATTR{ro}=="0"
    ATTR{size}=="2147483648"
    ATTR{stat}=="     356        0    12806       43        1        0        0        0        0       46       43        0        0        0        0        1        0"
    ATTR{trace/act_mask}=="disabled"
    ATTR{trace/enable}=="0"
    ATTR{trace/end_lba}=="disabled"
    ATTR{trace/pid}=="disabled"
    ATTR{trace/start_lba}=="disabled"

  looking at parent device '/devices/pci0000:80/0000:80:02.0/0000:82:00.0/host3/rport-3:0-4/target3:0:0/3:0:0:2':
    KERNELS=="3:0:0:2"
    SUBSYSTEMS=="scsi"
    DRIVERS=="sd"
    ATTRS{blacklist}==""
    ATTRS{delete}=="(not readable)"
    ATTRS{device_blocked}=="0"
    ATTRS{device_busy}=="0"
    ATTRS{dh_state}=="detached"
    ATTRS{eh_timeout}=="10"
    ATTRS{evt_capacity_change_reported}=="0"
    ATTRS{evt_inquiry_change_reported}=="0"
    ATTRS{evt_lun_change_reported}=="0"
    ATTRS{evt_media_change}=="0"
    ATTRS{evt_mode_parameter_change_reported}=="0"
    ATTRS{evt_soft_threshold_reached}=="0"
    ATTRS{inquiry}==""
    ATTRS{iocounterbits}=="32"
    ATTRS{iodone_cnt}=="0x201"
    ATTRS{ioerr_cnt}=="0x3"
    ATTRS{iorequest_cnt}=="0x201"
    ATTRS{iotmo_cnt}=="0x0"
    ATTRS{model}=="QUANTASTOR      "
    ATTRS{power/autosuspend_delay_ms}=="-1"
    ATTRS{power/control}=="on"
    ATTRS{power/runtime_active_time}=="41551863"
    ATTRS{power/runtime_status}=="active"
    ATTRS{power/runtime_suspended_time}=="0"
    ATTRS{queue_depth}=="64"
    ATTRS{queue_ramp_up_period}=="120000"
    ATTRS{queue_type}=="simple"
    ATTRS{rescan}=="(not readable)"
    ATTRS{rev}=="380 "
    ATTRS{scsi_level}=="7"
    ATTRS{state}=="running"
    ATTRS{timeout}=="30"
    ATTRS{type}=="0"
    ATTRS{vendor}=="OSNEXUS "
    ATTRS{vpd_pg0}==""
    ATTRS{vpd_pg80}==""
    ATTRS{vpd_pg83}==""
    ATTRS{vpd_pgb0}==""
    ATTRS{vpd_pgb1}==""
    ATTRS{vpd_pgb2}==""
    ATTRS{wwid}=="naa.620000007355abb3b8950167b5790928"

  looking at parent device '/devices/pci0000:80/0000:80:02.0/0000:82:00.0/host3/rport-3:0-4/target3:0:0':
    KERNELS=="target3:0:0"
    SUBSYSTEMS=="scsi"
    DRIVERS==""
    ATTRS{power/control}=="auto"
    ATTRS{power/runtime_active_time}=="41551863"
    ATTRS{power/runtime_status}=="active"
    ATTRS{power/runtime_suspended_time}=="0"

  looking at parent device '/devices/pci0000:80/0000:80:02.0/0000:82:00.0/host3/rport-3:0-4':
    KERNELS=="rport-3:0-4"
    SUBSYSTEMS==""
    DRIVERS==""
    ATTRS{power/control}=="auto"
    ATTRS{power/runtime_active_time}=="0"
    ATTRS{power/runtime_status}=="unsupported"
    ATTRS{power/runtime_suspended_time}=="0"

  looking at parent device '/devices/pci0000:80/0000:80:02.0/0000:82:00.0/host3':
    KERNELS=="host3"
    SUBSYSTEMS=="scsi"
    DRIVERS==""
    ATTRS{power/control}=="auto"
    ATTRS{power/runtime_active_time}=="106"
    ATTRS{power/runtime_status}=="suspended"
    ATTRS{power/runtime_suspended_time}=="41554309"

  looking at parent device '/devices/pci0000:80/0000:80:02.0/0000:82:00.0':
    KERNELS=="0000:82:00.0"
    SUBSYSTEMS=="pci"
    DRIVERS=="lpfc"
    ATTRS{ari_enabled}=="1"
    ATTRS{broken_parity_status}=="0"
    ATTRS{class}=="0x0c0400"
    ATTRS{consistent_dma_mask_bits}=="64"
    ATTRS{current_link_speed}=="8.0 GT/s PCIe"
    ATTRS{current_link_width}=="8"
    ATTRS{d3cold_allowed}=="1"
    ATTRS{device}=="0xe300"
    ATTRS{dma_mask_bits}=="64"
    ATTRS{driver_override}=="(null)"
    ATTRS{enable}=="1"
    ATTRS{irq}=="132"
    ATTRS{local_cpulist}=="1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47"
    ATTRS{local_cpus}=="aaaa,aaaaaaaa"
    ATTRS{max_link_speed}=="8.0 GT/s PCIe"
    ATTRS{max_link_width}=="8"
    ATTRS{msi_bus}=="1"
    ATTRS{msi_irqs/133}=="msix"
    ATTRS{msi_irqs/134}=="msix"
    ATTRS{msi_irqs/135}=="msix"
    ATTRS{msi_irqs/136}=="msix"
    ATTRS{msi_irqs/137}=="msix"
    ATTRS{msi_irqs/138}=="msix"
    ATTRS{msi_irqs/139}=="msix"
    ATTRS{msi_irqs/140}=="msix"
    ATTRS{msi_irqs/141}=="msix"
    ATTRS{msi_irqs/142}=="msix"
    ATTRS{msi_irqs/143}=="msix"
    ATTRS{msi_irqs/144}=="msix"
    ATTRS{msi_irqs/145}=="msix"
    ATTRS{msi_irqs/146}=="msix"
    ATTRS{msi_irqs/147}=="msix"
    ATTRS{msi_irqs/148}=="msix"
    ATTRS{msi_irqs/149}=="msix"
    ATTRS{msi_irqs/150}=="msix"
    ATTRS{msi_irqs/151}=="msix"
    ATTRS{msi_irqs/152}=="msix"
    ATTRS{msi_irqs/153}=="msix"
    ATTRS{msi_irqs/154}=="msix"
    ATTRS{msi_irqs/155}=="msix"
    ATTRS{msi_irqs/156}=="msix"
    ATTRS{numa_node}=="1"
    ATTRS{power/control}=="on"
    ATTRS{power/runtime_active_time}=="41557831"
    ATTRS{power/runtime_status}=="active"
    ATTRS{power/runtime_suspended_time}=="0"
    ATTRS{power/wakeup}=="disabled"
    ATTRS{power/wakeup_abort_count}==""
    ATTRS{power/wakeup_active}==""
    ATTRS{power/wakeup_active_count}==""
    ATTRS{power/wakeup_count}==""
    ATTRS{power/wakeup_expire_count}==""
    ATTRS{power/wakeup_last_time_ms}==""
    ATTRS{power/wakeup_max_time_ms}==""
    ATTRS{power/wakeup_total_time_ms}==""
    ATTRS{power_state}=="D0"
    ATTRS{remove}=="(not readable)"
    ATTRS{rescan}=="(not readable)"
    ATTRS{reset}=="(not readable)"
    ATTRS{reset_method}=="flr bus"
    ATTRS{revision}=="0x01"
    ATTRS{sriov_drivers_autoprobe}=="1"
    ATTRS{sriov_numvfs}=="0"
    ATTRS{sriov_offset}=="2"
    ATTRS{sriov_stride}=="1"
    ATTRS{sriov_totalvfs}=="16"
    ATTRS{sriov_vf_device}=="e300"
    ATTRS{sriov_vf_total_msix}=="0"
    ATTRS{subsystem_device}=="0xe332"
    ATTRS{subsystem_vendor}=="0x10df"
    ATTRS{vendor}=="0x10df"

  looking at parent device '/devices/pci0000:80/0000:80:02.0':
    KERNELS=="0000:80:02.0"
    SUBSYSTEMS=="pci"
    DRIVERS=="pcieport"
    ATTRS{acpi_index}=="20"
    ATTRS{aer_rootport_total_err_cor}=="0"
    ATTRS{aer_rootport_total_err_fatal}=="0"
    ATTRS{aer_rootport_total_err_nonfatal}=="0"
    ATTRS{ari_enabled}=="0"
    ATTRS{broken_parity_status}=="0"
    ATTRS{class}=="0x060400"
    ATTRS{consistent_dma_mask_bits}=="32"
    ATTRS{current_link_speed}=="8.0 GT/s PCIe"
    ATTRS{current_link_width}=="8"
    ATTRS{d3cold_allowed}=="1"
    ATTRS{device}=="0x2f04"
    ATTRS{dma_mask_bits}=="32"
    ATTRS{driver_override}=="(null)"
    ATTRS{enable}=="1"
    ATTRS{irq}=="34"
    ATTRS{label}=="SLOT 4"
    ATTRS{local_cpulist}=="1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47"
    ATTRS{local_cpus}=="aaaa,aaaaaaaa"
    ATTRS{max_link_speed}=="8.0 GT/s PCIe"
    ATTRS{max_link_width}=="16"
    ATTRS{msi_bus}=="1"
    ATTRS{msi_irqs/34}=="msi"
    ATTRS{numa_node}=="1"
    ATTRS{power/autosuspend_delay_ms}=="100"
    ATTRS{power/control}=="auto"
    ATTRS{power/runtime_active_time}=="41557839"
    ATTRS{power/runtime_status}=="active"
    ATTRS{power/runtime_suspended_time}=="0"
    ATTRS{power/wakeup}=="enabled"
    ATTRS{power/wakeup_abort_count}=="0"
    ATTRS{power/wakeup_active}=="0"
    ATTRS{power/wakeup_active_count}=="0"
    ATTRS{power/wakeup_count}=="0"
    ATTRS{power/wakeup_expire_count}=="0"
    ATTRS{power/wakeup_last_time_ms}=="0"
    ATTRS{power/wakeup_max_time_ms}=="0"
    ATTRS{power/wakeup_total_time_ms}=="0"
    ATTRS{power_state}=="D0"
    ATTRS{remove}=="(not readable)"
    ATTRS{rescan}=="(not readable)"
    ATTRS{revision}=="0x02"
    ATTRS{secondary_bus_number}=="130"
    ATTRS{subordinate_bus_number}=="131"
    ATTRS{subsystem_device}=="0x0000"
    ATTRS{subsystem_vendor}=="0x8086"
    ATTRS{vendor}=="0x8086"

  looking at parent device '/devices/pci0000:80':
    KERNELS=="pci0000:80"
    SUBSYSTEMS==""
    DRIVERS==""
    ATTRS{power/control}=="auto"
    ATTRS{power/runtime_active_time}=="0"
    ATTRS{power/runtime_status}=="unsupported"
    ATTRS{power/runtime_suspended_time}=="0"
    ATTRS{power/wakeup}=="disabled"
    ATTRS{power/wakeup_abort_count}==""
    ATTRS{power/wakeup_active}==""
    ATTRS{power/wakeup_active_count}==""
    ATTRS{power/wakeup_count}==""
    ATTRS{power/wakeup_expire_count}==""
    ATTRS{power/wakeup_last_time_ms}==""
    ATTRS{power/wakeup_max_time_ms}==""
    ATTRS{power/wakeup_total_time_ms}==""
    ATTRS{waiting_for_supplier}=="0"


```
