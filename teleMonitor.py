import os, sys, platform, signal, argparse, logging,  threading, time;

import telegram;
from telegram.ext import Updater, CommandHandler, CallbackContext;

from cMonitor import cMonitor;

global tele;
global logmon;
global monThread;
global logger;

# LOG FOR MONITOER #
class cLogMonitor:
	rateCPU = [];
	rateMEM = [];

	def __init__(self):
		self.rateCPU = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
		self.rateMEM = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
		pass;

	def __del__(self):
		pass;
# LOG FOR MONITOER #

# TELEGRAM BOT ASSIST CLASS #
class cTelegramBot:
	__bot = None;
	__botCid = None;
	__updater = None;
	__masterList = [];

	def __init__(self, key, masters=None, cid=None):
		try:
			self.__bot = telegram.Bot(token=key);
			self.__updater = Updater(token=key);
			self.__masterList = masters;

			if(cid is not None):	self.__botCid = cid;
			elif(cid is None and self.__masterList):	self.__botCid = self.__masterList[0];
			else:	self.__botCid = self.__bot.getUpdates()[-1].message.chat.id;
		except Exception as e:	logger.error(e);
		pass;

	def __del__(self):
		try:	self.__updater.stop();
		except Exception as e:	logger.error(e);
		pass;

	## Start ##
	def start(self):
		self.__updater.start_polling();
		self.__updater.idle();

	## Reg new update command ##
	def setUpdaterEvent(self, event, function, pass_args=False):	self.__updater.dispatcher.add_handler(CommandHandler(event, function, pass_args=pass_args));

	def botSendMessage(self, msg):	self.__bot.sendMessage(chat_id=self.__botCid, text=msg);
	def botReplyMessage(self, msg):	self.__updater.message.reply_text(msg);

	def botCmdSecure(self, update):
		if(not self.__masterList or update.message.from_user.id in self.__masterList):	return True;
		else:	return False;
# TELEGRAM BOT ASSIST CLASS #

# TELEGRAM BOT COMMAND EVENT HANDLER #
## HELP COMMAND CALLBACK ##
def onCommandHelp(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	helpMsg  = "------------ HelP ------------\n";
	helpMsg += " * CPU 관련\n";
	helpMsg += "    - 정보		: /cpu_info\n";
	helpMsg += "    - 사용량		: /cpu_use\n";
	helpMsg += " * Memory 관련\n";
	helpMsg += "    - 사용량		: /mem_use\n";
	helpMsg += " * Disk 관련\n";
	helpMsg += "    - 정보		: /disk_info\n";
	helpMsg += "    - 사용량		: /disk_use\n";
	helpMsg += " * Network 관련\n";
	helpMsg += "    - 정보		: /net_info\n";
	helpMsg += "    - 세부정보	: /net_detail\n";
	helpMsg += " * Process 관련\n";
	helpMsg += "    - 정보		: /process_info\n";
	helpMsg += " * 기타\n";
	helpMsg += "    - 온도		: /temperature\n";
	helpMsg += "    - 팬			: /fans\n";
	helpMsg += "    - 배터리		: /battery\n";
	helpMsg += "    - 부팅 시간	: /boottime\n";
	helpMsg += "    - 접속자		: /users\n";
	helpMsg += "------------------------------\n";
	update.message.reply_text(helpMsg);

def onCommandCPUInfo(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.cpu_info();

	msg  = "* CPU INFO\n";
	msg += "   - Physical Core : %d\n" % mInfo['pCore'];
	msg += "   - Logical Core : %d\n" % mInfo['lCore'];
	msg += "   - CPU Frequency : {} GHz\n".format( round(mInfo['freq'][0]/1024, 1) );
	update.message.reply_text(msg);

def onCommandCPUUse(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.using_cpu_info();

	msg  = "* CPU USE\n";
	msg += "   - User	: {}%\n".format( mInfo[0] );
	msg += "   - System	: {}%\n".format( mInfo[2] );
	msg += "   - idle	: {}%\n".format( mInfo[3] );
	update.message.reply_text(msg);

def onCommandMemoryInfo(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.using_mem_info();

	msg  = "* MEMORY USE\n";
	msg += "   - [Physical]	Total : %4.1fG, Used : %4.1fG, Free : %4.1fG, Avaliable : %4.1fG\n" % (mInfo['physical'][0]/1024**3, mInfo['physical'][3]/1024**3, mInfo['physical'][4]/1024**3, mInfo['physical'][1]/1024**3);
	msg += "   - [Swap]		Total : %4.1fG, Used : %4.1fG, Free : %4.1fG\n" % (mInfo['swap'][0]/1024**3, mInfo['swap'][1]/1024**3, mInfo['swap'][2]/1024**3);
	update.message.reply_text(msg);

def onCommandNetInfo(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.net_info();

	msg  = "* NETWORK INFO\n";
	for k in mInfo['device'].keys():	msg += "   - [%s]	Speed : %d, MTU : %d\n" % (k, mInfo['device'][k][2], mInfo['device'][k][3]);

	if(mInfo['state'][2] > 1000000):	msg += "   - Send : %.0fG packets (%.1fGB)\n" % (mInfo['state'][2]/1000000, mInfo['state'][0]/1024**3);
	elif(mInfo['state'][2] > 1000):		msg += "   - Send : %.0fK packets (%.1fGB)\n" % (mInfo['state'][2]/1000, mInfo['state'][0]/1024**3);
	else:	msg += "   - Send : %.0f packets (%.1fGB)\n" % (mInfo['state'][2], mInfo['state'][0]/1024**3);

	if(mInfo['state'][3] > 1000000):	msg += "   - Recv : %.0fG packets (%.1fGB)\n" % (mInfo['state'][3]/1000000, mInfo['state'][1]/1024**3);
	elif(mInfo['state'][3] > 1000):		msg += "   - Recv : %.0fK packets (%.1fGB)\n" % (mInfo['state'][3]/1000, mInfo['state'][1]/1024**3);
	else:	msg += "   - Recv : %.0f packets (%.1fGB)\n" % (mInfo['state'][3], mInfo['state'][1]/1024**3);
	update.message.reply_text(msg);

def onCommandNetDetail(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.detail_net_info();

	msg  = "* NETWORK DETAIL\n";
	msg += "%5s %10s %17s:%5s %10s\n" % ("pid", "name", "IP", "port", "status");
	for k in mInfo.keys():
		msg += "%5d %10s %17s:%d %10s" % (k, mInfo[k]['name'], mInfo[k]['raddr'][0], mInfo[k]['raddr'][1], mInfo[k]['status']);
	update.message.reply_text(msg);

def onCommandTemperature(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.temperature_info();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* TEMPERATURE\n";

	update.message.reply_text(msg);

def onCommandFans(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.fans_info();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* FAN DETAIL\n";

	update.message.reply_text(msg);

def onCommandBattery(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.battery_info();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* BATTERY DETAIL\n";

	update.message.reply_text(msg);

def onCommandBoottime(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.boot_time();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* BOOT TIME\n";
		msg += "   - {}".format(mInfo);

	update.message.reply_text(msg);

def onCommandConnectedUsers(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.connect_user();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* CONNECTED USER INFO\n";
		msg += "%6s %10s %7s %17s\n" % ("PID", "USER", "PTS", "IP");
		for i in range(len(mInfo)):
			msg += "%6d %10s %7s %17s\n" % (mInfo[i].pid, mInfo[i].name, mInfo[i].terminal, mInfo[i].host);

	update.message.reply_text(msg);

def onCommandProcess(update: telegram.Update, _: CallbackContext) -> None:
	if(not tele.botCmdSecure(update)):	return ;

	monitor = cMonitor();
	mInfo = monitor.process_info();

	msg  = "* PROCESS DETAIL\n";
	msg += "%5s%5s %25s %10s\n" % ("PID", "PPID", "NAME", "STATUS");

	cnt = 0;
	for proc in mInfo:
		msg += "%5d%5d %25s% 10s\n" % (proc.info['pid'], proc.info['ppid'], proc.info['name'], proc.info['status']);
		cnt += 1;
		if(cnt >= 30):
			update.message.reply_text(msg);
			msg = "%5s%5s  %25s %10s\n" % ("PID", "PPID", "NAME", "STATUS");
			cnt = 0;

def onCommandMyTelegramID(update: telegram.Update, _: CallbackContext) -> None:
	msg  = "* USER ID : %s, FID : %s" % (update.message.from_user.name, str(update.message.from_user.id));
	update.message.reply_text(msg);

def onCommandMyChatroomID(update: telegram.Update, _: CallbackContext) -> None:
	msg  = "* Chat title : %s, CID : %s" % (update.message.chat.title, str(update.message.chat.id));
	update.message.reply_text(msg);

# TELEGRAM BOT COMMAND EVENT HANDLER #

# TIMMER`S FUNCTION #
def THRTIME_monitoringCPU():
	monitor = cMonitor();
	try:	del logmon.rateCPU[0];
	except:	pass;
	logmon.rateCPU.append(monitor.using_cpurate());

	if(logmon.rateCPU[-1] >= args.overheatcpu or abs(logmon.rateCPU[-1]-logmon.rateCPU[-2]) >= args.diffcpu):
		tele.botSendMessage("*CPU usage is {}%.".format(logmon.rateCPU[-1]));
		pass;

	monThread.append(threading.Timer((args.termonitor * 60), THRTIME_monitoringCPU));
	monThread[-1].start();
	logger.info("  - CPU Monitoring Thread Start.");

def THRTIME_monitoringMEM():
	monitor = cMonitor();
	try:	del logmon.rateMEM[0];
	except:	pass;
	logmon.rateMEM.append(monitor.using_cpurate());

	if(logmon.rateMEM[-1] >= args.overheatmem or abs(logmon.rateMEM[-1]-logmon.rateMEM[-2]) >= args.diffmem):
		tele.botSendMessage("*Memory usage is {}%.".format(logmon.rateMEM[-1]));
		pass;

	monThread.append(threading.Timer((args.termonitor * 60), THRTIME_monitoringMEM));
	monThread[-1].start();
	logger.info("  - Memory Monitoring Thread Start.");
# TIMMER`S FUNCTION #


def terminate(signum, frame):
	for t in monThread:	t.cancel();
	del logmon;
	del tele;
	logger.info("Receive Signal {0}.".format(signum));
	logger.info("Terminating...");
	sys.exit(signum);


def main():
	#---------- Global ----------#
	global tele;
	global logmon;
	global monThread;
	#---------- Global ----------#

	monThread = [];

	tele = cTelegramBot(key=args.teltoken, masters=args.mastertoken, cid=args.chattoken);

	signal.signal(signal.SIGINT, terminate);
	signal.signal(signal.SIGTERM, terminate);

	if(args.termonitor > 0):
		logmon = cLogMonitor();
		THRTIME_monitoringCPU();
		THRTIME_monitoringMEM();
		pass;

	## MONITORING COMMNAD ##
	tele.setUpdaterEvent("help",			onCommandHelp);
	tele.setUpdaterEvent("cpu_info",		onCommandCPUInfo);
	tele.setUpdaterEvent("cpu_use",			onCommandCPUUse);
	tele.setUpdaterEvent("mem_use",			onCommandMemoryInfo);
	tele.setUpdaterEvent("net_info",		onCommandNetInfo);
	tele.setUpdaterEvent("net_detail",		onCommandNetDetail);
	tele.setUpdaterEvent("temperature",		onCommandTemperature);
	tele.setUpdaterEvent("fans",			onCommandFans);
	tele.setUpdaterEvent("battery",			onCommandBattery);
	tele.setUpdaterEvent("boottime",		onCommandBoottime);
	tele.setUpdaterEvent("users",			onCommandConnectedUsers);
	tele.setUpdaterEvent("process_info",	onCommandProcess);
	## MONITORING COMMNAD ##

	tele.setUpdaterEvent("whatismyuserid",	onCommandMyTelegramID);
	tele.setUpdaterEvent("whatismychatid",	onCommandMyChatroomID);

	logger.info("------ Start Tele ------");

	tele.start();
	## TELEGRAM SETTING ##

	pass;

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Process some integers.');
	parser.add_argument('-d', '--demon', dest='demon', action='store_true', default=False, help="Run on demon.");
	parser.add_argument('-o', '--os', dest='os', type=str, default=str(platform.system()), help="Select OS. (Default:%s)" % str(platform.system()));
	parser.add_argument('-t', '--telegram_token', dest='teltoken', type=str, default=None, help="Telegram Token.");
	parser.add_argument('-m', '--master_token', dest='mastertoken', type=str, default=None, help="Telegram master user token.");
	parser.add_argument('-c', '--chat_token', dest='chattoken', type=str, default=None, help="Telegram chat room token");
	parser.add_argument('--cpu_diff', dest='diffcpu', type=float, default=30, help="CPU DIFF.");
	parser.add_argument('--mem_diff', dest='diffmem', type=float, default=25, help="MEMORY DIFF.");
	parser.add_argument('--cpu_overheat', dest='overheatcpu', type=float, default=85, help="Overheat CPU.");
	parser.add_argument('--mem_overheat', dest='overheatmem', type=float, default=80, help="Overheat Memory.");
	parser.add_argument('--term_monitor', dest='termonitor', type=int, default=5, help="Term monitoring. (0 is not monitoring) [Default:5min]");

	args = parser.parse_args();

	if(args.teltoken is None):
		try:
			fCfg = open('./telemonitor.cfg', 'r');
			aCfg = fCfg.read().splitlines();
			for cfg in aCfg:
				conf = cfg.split('=');
				if(conf[0] == 'telegram_token'):	args.teltoken = conf[1];
				if(conf[0] == 'master_token'):		args.mastertoken = conf[1];
				if(conf[0] == 'chat_token'):		args.chattoken = conf[1];
		except:	exit(0);
		pass;

	## LOGGER ##
	logging.basicConfig(level=logging.INFO, format='%(message)s');
	logger = logging.getLogger("TeleMonitor");
	logger.addHandler( logging.FileHandler("teleMonitor.logs") );
	## LOGGER ##


	logger.info('*' * 80);
	logger.info("* - Platform : %s" % args.os);
	logger.info("* - Secure CMD : %s" % ("True" if args.mastertoken else "False"));
	logger.info("* - Monitoring Term : %d min." % args.termonitor);
	logger.info("* - CPU change in %d minutes to notificiation : %.1f%%" % (args.termonitor, args.diffcpu));
	logger.info("* - Memory change in %d minutes to notificiation : %.1f%%" % (args.termonitor, args.diffmem));
	logger.info("* - Notification of overheat CPU usage : %.1f%%" % args.overheatcpu);
	logger.info("* - Notification of overheat Memory usage : %.1f%%" % args.overheatmem);
	logger.info('*' * 80);
	logger.info('');

	## Daemon ##
	if(args.demon):
		logger.info("  - Run Daemon mode.");

		import shutil;
		if(not os.path.exists("/opt/TelegramMonitoring")):
			os.mkdir("/opt/TelegramMonitoring");
		if(not os.path.exists("/opt/TelegramMonitoring/teleMonitor.py")):
			shutil.copy("teleMonitor.py", "/opt/TelegramMonitoring/teleMonitor.py");
			shutil.copy("cMonitor.py", "/opt/TelegramMonitoring/cMonitor.py");
			shutil.copy("telemonitor.cfg", "/opt/TelegramMonitoring/telemonitor.cfg");
		if(not os.path.exists("/etc/systemd/system/teleMonitor.service")):
			shutil.copy("teleMonitor.service", "/etc/systemd/system/teleMonitor.service");
			os.system("systemctl daemon-reload");
			print("Run daemon using 'systemctl start teleMonitor.service' command.");
			exit(0);

		pid = os.fork();
		if(pid > 0):	exit(0);
		else:
			os.chdir('/');
			os.setsid();
			os.umask(0);

			pid = os.fork();
			if(pid > 0):	exit(0);
			else:
				sys.stdout.flush();
				sys.stderr.flush();

				si = open(os.devnull, 'r');
				so = open(os.devnull, 'a+');
				se = open(os.devnull, 'a+');

				os.dup2(si.fileno(), sys.stdin.fileno());
				os.dup2(so.fileno(), sys.stdout.fileno());
				os.dup2(se.fileno(), sys.stderr.fileno());

				with open("/var/run/teleMonitor.pid", "w") as pid_file:		pid_file.write(str(os.getpid()));

				exit_code = main();
				exit(exit_code);

	else:	main();
	## Daemon ##
	pass;