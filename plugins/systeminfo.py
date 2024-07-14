# 导入psutil库
import platform

import psutil


# 定义一个函数，将字节转换为合适的单位
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


# 定义一个函数，获取并返回系统信息
def get_system_info():
    # 创建一个空列表，用于存储系统信息
    system_info = ["=" * 6 + "System Info" + "=" * 6 + "\n"]
    # 获取系统信息
    uname = platform.uname()
    system_info.append(f"System: {uname.system}\n")
    system_info.append(f"Node Name: {uname.node}\n")
    system_info.append(f"Release: {uname.release}\n")
    system_info.append(f"Version: {uname.version}\n")
    system_info.append(f"Machine: {uname.machine}\n")
    system_info.append(f"Processor: {uname.processor}\n")
    # 获取CPU信息
    system_info.append("=" * 6 + "CPU Info" + "=" * 6 + "\n")
    # 核心数
    system_info.append(f"Physical cores: {psutil.cpu_count(logical=False)}\n")
    system_info.append(f"Total cores: {psutil.cpu_count(logical=True)}\n")
    # CPU频率
    cpufreq = psutil.cpu_freq()
    system_info.append(f"Max Frequency: {cpufreq.max:.2f}Mhz\n")
    system_info.append(f"Min Frequency: {cpufreq.min:.2f}Mhz\n")
    system_info.append(f"Current Frequency: {cpufreq.current:.2f}Mhz\n")
    # CPU使用率
    system_info.append("CPU Usage Per Core:\n")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        system_info.append(f"Core {i}: {percentage}%\n")
    system_info.append(f"Total CPU Usage: {psutil.cpu_percent()}%\n")
    '''# CPU温度
    system_info.append("CPU Temperature:")
    sensors_temperatures = psutil.sensors_temperatures()
    for name, entries in sensors_temperatures.items():
        system_info.append(f"{name}:")
        for entry in entries:
            system_info.append(f"    {entry.label or 'N/A'}: {entry.current}°C")'''
    # 获取内存信息
    system_info.append("=" * 6 + "Memory Info" + "=" * 6 + "\n")
    # 获取内存总量，使用量，空闲量和使用百分比
    svmem = psutil.virtual_memory()
    system_info.append(f"Total: {get_size(svmem.total)}\n")
    system_info.append(f"Available: {get_size(svmem.available)}\n")
    system_info.append(f"Used: {get_size(svmem.used)}\n")
    system_info.append(f"Percentage: {svmem.percent}%\n")
    # 获取当前网络接口的IO统计
    system_info.append("=" * 6 + "NetWork IO" + "=" * 6 + "\n")
    net_io = psutil.net_io_counters()
    system_info.append(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}\n")
    system_info.append(f"Total Bytes Received: {get_size(net_io.bytes_recv)}\n")
    # 获取硬盘信息
    system_info.append("=" * 6 + "Disk Info" + "=" * 6 + "\n")
    system_info.append(f"=== Disk IO===\n")
    disk_io = psutil.disk_io_counters()
    system_info.append(f"Total read: {get_size(disk_io.read_bytes)}\n")
    system_info.append(f"Total write: {get_size(disk_io.write_bytes)}\n")
    # 获取网络信息
    '''system_info.append("="*6 + "Network Information" + "="*6)
    # 获取所有网络接口的详细信息
    system_info.append("All network interfaces and their details:")
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            system_info.append(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                system_info.append(f"  IP Address: {address.address}")
                system_info.append(f"  Netmask: {address.netmask}")
                system_info.append(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                system_info.append(f"  MAC Address: {address.address}")
                system_info.append(f"  Netmask: {address.netmask}")
                system_info.append(f"  Broadcast MAC: {address.broadcast}")'''

    # 获取硬盘分区和使用情况
    system_info.append("Partitions and Usage:\n")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        system_info.append(f"=== Device: {partition.device} ===\n")
        system_info.append(f"  Mountpoint: {partition.mountpoint}\n")
        system_info.append(f"  File system type: {partition.fstype}\n")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # 这可能是由于没有访问权限造成的
            continue
        system_info.append(f"  Total Size: {get_size(partition_usage.total)}\n")
        system_info.append(f"  Used: {get_size(partition_usage.used)}\n")
        system_info.append(f"  Free: {get_size(partition_usage.free)}\n")
        system_info.append(f"  Percentage: {partition_usage.percent}%\n")
    # 获取硬盘总的IO统计

    # 返回系统信息列表
    return system_info

# 调用函数，打印结果
#info = get_system_info()
#for line in info:
#print(line)
