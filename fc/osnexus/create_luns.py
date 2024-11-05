import asyncio
import json
import os
from os import path
import re
from tkinter.font import names

import requests
import traceback
import openshift_client as oc
from openshift_client import OpenShiftPythonException, Context, Result
from concurrent.futures import ProcessPoolExecutor
from quantastor.qs_client import QuantastorClient
from fc.osnexus.utils import run_in_executor
from utils.timer import Timer

NUM_LUNS = 260
LUN_NAME_PREFIX = "API.LUN"
QUANTASTOR_IP = "172.16.1.119"
QUANTASTOR_USER = "admin"
QUANTASTOR_PASS ="Welcome11"
TEST_HOST = "r730ocp5.localdomain"
THIS_FILE_DIR = os.path.dirname(os.path.realpath(__file__))


def get_luns(client: QuantastorClient, verbose: bool = False):
    luns = []
    for lun in client.storage_volume_enum():
        lun_json = lun.exportJson()
        if verbose:
            luns.append(lun_json)
        else:
            if "name" in lun_json and lun_json["name"]:
                luns.append(lun_json["name"])
    if luns:
        return luns


# # Batch delete LUNs once OSNEXUS fixes bug
# def delete_luns(client: QuantastorClient, lun_names: list, continue_if_fail: bool = False):
#     san_luns = get_luns(client)
#     # print(san_luns)
#
#     luns_to_delete = [lun_name for lun_name in lun_names if lun_name in san_luns]
#     try:
#         if luns_to_delete:
#             client.storage_volume_delete(storageVolumeList=luns_to_delete, flags=2)
#             print(f"Deleted luns: {luns_to_delete}")
#     except Exception as e:
#         print(f"Error attempting to delete luns: {e}")
#         if continue_if_fail:
#             exit()

def delete_luns(client: QuantastorClient, lun_names: list[str], exit_on_fail: bool = False):
    san_luns = get_luns(client)
    # print(san_luns)

    luns_to_delete = [lun_name for lun_name in lun_names if lun_name in san_luns]
    for lun_name in luns_to_delete:
        with Timer() as t:
            try:
                client.storage_volume_delete_ex(storageVolume=lun_name, flags=2)
                print(f"Deleted LUN: {lun_name}, Total Time: {t.stop():0.4f}s")
            except Exception as e:
                print(f"Error attempting to delete LUNs: {e}, Total Time: {t.stop():0.4f}s")
                if exit_on_fail:
                    exit()


def create_luns(client: QuantastorClient, count: int, lun_names: str|list[str]):
    with Timer() as t:
        try:
            client.storage_volume_create_ex(
                name=f'{LUN_NAME_PREFIX}',
                provisionableId='tank',
                size='1GiB',
                count=f'{count}',
                blockSizeKb='64',
                compressionType='on',
                copies='0',
                profile='c43618f3-25c9-bfd2-7fea-6706ca70f835'
            )

            client.storage_volume_acl_add_remove_ex(storageVolumeList=lun_names, host=TEST_HOST, modType=0)
            print(f"Created {count} LUNs, Total Time: {t.stop():0.4f}s")
        except Exception as e:
            print(f"Error attempting to create LUNs: {e}, Total Time: {t.stop():0.4f}s")

def debug_pod_exec(operation: str, node_name: str, stdin_str: str, tracker: Context = None):
    r = Result(operation)
    r.add_action(oc.oc_action(oc.cur_context(), "debug", cmd_args=[f"node/{node_name}"], stdin_str=stdin_str))
    if tracker:
        print(f"Tracker: {tracker.get_result()}")
    return r.out().strip(), r.err().strip()

async def main():
    # client = QuantastorClient(QUANTASTOR_IP, QUANTASTOR_USER, QUANTASTOR_PASS, timeout=1200)
    # # system = client.storage_system_get()
    # # print(json.dumps(system.exportJson(), sort_keys=True, indent=4, separators=(',', ': ')))
    #
    # # task = client.task_get(id="9ff2c0bf-5fb4-c414-4b3f-4b4d8be67c62")
    # # print(json.dumps(task.exportJson(), sort_keys=True, indent=4, separators=(',', ': ')))
    #
    # # Clean up prior LUNs
    # if NUM_LUNS > 1:
    #     lun_names = [f'{LUN_NAME_PREFIX}.{lun_id:03}' for lun_id in range(NUM_LUNS)]
    # else:
    #     lun_names = [f'{LUN_NAME_PREFIX}']
    #
    # delete_luns(client, lun_names)
    #
    # # Build LUNs on array
    # create_luns(client, NUM_LUNS, lun_names)
    # # print(json.dumps(get_luns(client, verbose=True), sort_keys=True, indent=4, separators=(',', ': ')))


    # Run operations in a debug pod on OCP
    oc_context = Context()
    oc_context.set_default_skip_tls_verify = True
    oc_context.oc_path = f"{THIS_FILE_DIR}\\oc.exe"
    oc_context.kubeconfig_path = f"{THIS_FILE_DIR}\\kubeconfig"
    oc_context.token = "sha256~osw2Pge9NdDJdAKvej3rn6rsu8zJBkHs1M_nFZqX7d4"
    oc_context.api_server = "https://api.ocp.sno.localdomain:6443"

    with oc.timeout(60 * 30), oc.tracking() as tracker, oc_context:
        if oc.get_config_context() is None:
            print(f'Current context not set! Logging into API server: {oc_context.api_server}')
            try:
                oc.invoke('login')
            except OpenShiftPythonException:
                print('error occurred logging into API Server')
                traceback.print_exc()
                print(f'Tracking:\n{tracker.get_result().as_json(redact_streams=False)}\n\n')
                exit(1)

        print(f'Current oc context: {oc.get_config_context().strip()}')

        try:
            # print(f"Found: {len(oc.selector('pods').objects())} pods")
            # print(f"Current project: {oc.get_project_name()}")

            # get_scsi_hosts_out, get_scsi_hosts_err = debug_pod_exec(
            #     operation="get_scsi_hosts",
            #     node_name=TEST_HOST,
            #     stdin_str="ls /sys/class/scsi_host | grep host")
            #
            # if get_scsi_hosts_out:
            #     # print(get_scsi_hosts_out)
            #     for host_id in get_scsi_hosts_out.splitlines():
            #         rescan_out, rescan_err = debug_pod_exec(
            #             operation=f"recan_{host_id}",
            #             node_name=TEST_HOST,
            #             stdin_str=f"(time echo '- - -' > /sys/class/scsi_host/{host_id}/scan) 2> >( tee /dev/stderr ) | grep real | awk '{{print $2}}'")
            #         print(f"Rescanned {host_id} in: {rescan_out}")

            natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

            ls_disk_by_path_out, ls_disk_by_path_err = debug_pod_exec(
                operation=f"ls_disk_by_path",
                node_name=TEST_HOST,
                stdin_str="ls /host/dev/disk/by-path/")

            if ls_disk_by_path_err:
                print(ls_disk_by_path_err)

            ls_disk_by_path_out = ls_disk_by_path_out.splitlines()
            # print(ls_disk_by_path_out)
            ls_disk_by_path_out = sorted(ls_disk_by_path_out, key=natsort)
            print(f"Disks by path:")
            for by_path in ls_disk_by_path_out:
                print(by_path)
            print()

            ls_disk_by_id_out, ls_disk_by_id_err = debug_pod_exec(
                operation=f"ls_disk_by_id",
                node_name=TEST_HOST,
                stdin_str="ls /host/dev/disk/by-id/")

            if ls_disk_by_id_err:
                print(ls_disk_by_id_err)

            ls_disk_by_id_out = ls_disk_by_id_out.splitlines()
            # print(ls_disk_by_id_out)
            ls_disk_by_id_out = sorted(ls_disk_by_id_out, key=natsort)
            print(f"Disks by ID:")
            for by_id in ls_disk_by_id_out:
                print(by_id)
            print()

            def parse_lun_list(lun_num: str):
                wwn = "100000109bc3914e-0x21000024ff1e85b6"

                test_lun_name = "fc-0x" + wwn + "-lun-" + lun_num
                print(f"Testing contains for {test_lun_name}:")
                for lun in ls_disk_by_path_out:
                    if test_lun_name in lun:
                        print(lun)
                print()

                test_lun_regex = "^(pci-.*-fc|fc)-0x" + wwn + "-lun-" + lun_num + "$"
                print(f"Testing REGEX expression {test_lun_regex}:")
                for lun in ls_disk_by_path_out:
                    x = re.search(test_lun_regex, lun)
                    if x is not None:
                        print(x.group())
                print()

            parse_lun_list("260")
            # parse_lun_list("1")
            # parse_lun_list("11")

        except OpenShiftPythonException:
            print('Error occurred getting pods')
            traceback.print_exc()
            print(f'Tracking:\n{tracker.get_result().as_json(redact_streams=False)}\n\n')
if __name__ == "__main__":
    asyncio.run(main())
