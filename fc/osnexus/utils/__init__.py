import asyncio
import platform
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
from typing import Optional, Union


def print_ex(e, error_banner="Error", add_details=None):
    add_details_str = f"\nAdditional Details: {add_details}" if add_details else ""
    error_strs = [
        f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S.%f')[:-3]}]\n{error_banner} {str(e)}{add_details_str}\nStacktrace:",
        *traceback.format_exception(None, e, e.__traceback__)
    ]
    return "".join(error_strs)


# NOTE: https://stackoverflow.com/questions/30926840/how-to-check-change-between-two-values-in-percent
def get_perc_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


async def run_in_executor(executor: Optional[Union[ThreadPoolExecutor, ProcessPoolExecutor]] = None, *args, **kwargs):
    return await asyncio.get_running_loop().run_in_executor(executor, *args, **kwargs)


def chunks(lst, n):
    """
    Yield successive n-sized chunks from list.

    Note:
        Taken from https://stackoverflow.com/a/312464
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_p_and_l(entry_price, exit_price, direction):
    if entry_price == exit_price:
        return 0
    try:
        if direction.lower() == "long":
            return ((exit_price - entry_price) / entry_price) * 100.0
        elif direction.lower() == "short":
            return ((entry_price - exit_price) / entry_price) * 100.0
    except ZeroDivisionError:
        return float('inf')


def whoami():
    return sys._getframe(1).f_code.co_name


def delete_keys_with_none_value(_dict):
    """Delete None values recursively from all the dictionaries: https://stackoverflow.com/a/66127889"""
    for key, value in list(_dict.items()):
        if isinstance(value, dict):
            delete_keys_with_none_value(value)
        elif value is None:
            del _dict[key]
        elif isinstance(value, list):
            for v_i in value:
                if isinstance(v_i, dict):
                    delete_keys_with_none_value(v_i)

    return _dict


"""
Below is all from here: https://fredrikaverpil.github.io/2017/06/20/async-and-await-with-subprocesses/
"""


async def run_command(*args):
    """Run command in subprocess.

    Example from:
        http://asyncio.readthedocs.io/en/latest/subprocess.html
    """
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Status
    print("Started: %s, pid=%s" % (args, process.pid), flush=True)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    if process.returncode == 0:
        print(
            "Done: %s, pid=%s, result: %s"
            % (args, process.pid, stdout.decode().strip()),
            flush=True,
        )
    else:
        print(
            "Failed: %s, pid=%s, result: %s"
            % (args, process.pid, stderr.decode().strip()),
            flush=True,
        )

    # Result
    result = stdout.decode().strip()

    # Return stdout
    return result


async def run_command_shell(command):
    """Run command in subprocess (shell).

    Note:
        This can be used if you wish to execute e.g. "copy"
        on Windows, which can only be executed in the shell.
    """
    # Create subprocess
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Status
    print("Started:", command, "(pid = " + str(process.pid) + ")", flush=True)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    if process.returncode == 0:
        print("Done:", command, "(pid = " + str(process.pid) + ")", flush=True)
    else:
        print(
            "Failed:", command, "(pid = " + str(process.pid) + ")", flush=True
        )

    # Result
    result = stdout.decode().strip()

    # Return stdout
    return result


def run_asyncio_commands(tasks, max_concurrent_tasks=0):
    """Run tasks asynchronously using asyncio and return results.

    If max_concurrent_tasks are set to 0, no limit is applied.

    Note:
        By default, Windows uses SelectorEventLoop, which does not support
        subprocesses. Therefore ProactorEventLoop is used on Windows.
        https://docs.python.org/3/library/asyncio-eventloops.html#windows
    """
    all_results = []

    if max_concurrent_tasks == 0:
        all_chunks = [tasks]
        num_chunks = len(all_chunks)
    else:
        all_chunks = chunks(tasks, max_concurrent_tasks)
        num_chunks = len(list(chunks(tasks, max_concurrent_tasks)))

    if asyncio.get_event_loop().is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())

    loop = asyncio.get_event_loop()

    chunk = 1
    for tasks_in_chunk in all_chunks:
        print(
            "Beginning work on chunk %s/%s" % (chunk, num_chunks), flush=True
        )
        commands = asyncio.gather(*tasks_in_chunk)  # Unpack list using *
        results = loop.run_until_complete(commands)
        all_results += results
        print(
            "Completed work on chunk %s/%s" % (chunk, num_chunks), flush=True
        )
        chunk += 1

    return all_results
