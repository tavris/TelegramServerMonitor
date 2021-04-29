import os, psutil, subprocess, datetime;

class cMonitor:
	__os = "linux";

	def __init__(self, os="linux"):
		self.__os = os;
		pass;

	def __del__(self):
		pass;

	## CPU Information ##
	def cpu_info(self, logical=False):	return {'freq':psutil.cpu_freq(), 'pCore':psutil.cpu_count(logical=False), 'lCore':psutil.cpu_count(logical=True)};
	def using_cpu_info(self):	return psutil.cpu_times_percent(interval=None);
	def using_cpurate(self, interval=None):	return psutil.cpu_percent(interval=interval);
	## CPU Information ##

	## MEMORY Information ##
	def using_mem_info(self):	return {'physical':psutil.virtual_memory(), 'swap':psutil.swap_memory()};
	## MEMORY Information ##

	## DISK Information ##
	def disk_info(self):	return psutil.disk_partitions();
	def using_disk_info(self, path=None):
		pVal = {};
		if(path is not None):	pVal = psutil.disk_usage(path);
		else:
			partitions = psutil.disk_partitions();
			for partition in partitions:
				try:	pVal[partition.mountpoint] = psutil.disk_usage(partition.mountpoint);
				except:	pass;
		return pVal;
	## DISK Information ##

	## NETWORKS Information ##
	def net_info(self):	return {'device':psutil.net_if_stats(), 'state':psutil.net_io_counters()};
	def detail_net_info(self, connect=None):
		net = {};
		for conn in psutil.net_connections():
			if(conn.pid is not None):
				if(connect is None):	net[conn.pid] = {'raddr':conn.raddr, 'status':conn.status, 'family':conn.family};
				elif(conn.status == connect):	net[conn.pid] = {'raddr':conn.raddr, 'status':conn.status, 'family':conn.family};
				else:	pass;

		for proc in psutil.process_iter(['pid', 'name']):
			if(proc.pid in net.keys()):
				net[proc.pid]['name'] = proc.info['name'];

		return net;
	## NETWORKS Information ##

	## SENSORS Information ##
	def temperature_info(self):	return psutil.sensors_temperatures();
	def fans_info(self):	return psutil.sensors_fans();
	def battery_info(self):	return psutil.sensors_battery();
	## SENSORS Information ##

	## PROCESS Information ##
	### dic = ['cmdline', 'connections', 'cpu_affinity', 'cpu_num', 'cpu_percent', 'cpu_times', 'create_time', 'cwd', 'environ', 'exe', 'gids', 'io_counters', 'ionice', 'memory_full_info', 'memory_info', 'memory_maps', 'memory_percent', 'name', 'nice', 'num_ctx_switches', 'num_fds', 'num_handles', 'num_threads', 'open_files', 'pid', 'ppid', 'status', 'terminal', 'threads', 'uids', 'username'];
	def process_info(self, dic=['pid', 'ppid', 'name', 'username', 'cpu_percent', 'cpu_times', 'memory_percent', 'status']):	return psutil.process_iter(dic);
	## PROCESS Information ##

	## ETC Information ##
	def boot_time(self):	return datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S");
	def connect_user(self):	return psutil.users();
	## ETC Information ##