import os, sys, platform, signal, argparse, logging, threading, time;

import telegram;
from telegram.ext import Updater, CommandHandler, CallbackContext;

from cMonitor import cMonitor;
from teleHandler import *;

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
			self.__updater.dispatcher.add_error_handler(onCommonErrorHandler);
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

	def getJob(self):
		return self.__updater.job_queue;

	## Reg new update command ##
	def setUpdaterEvent(self, event, function, pass_args=False):
		logger.debug("  - Adding handler for Telegram comment event. (cmd : %s)" % event);
		self.__updater.dispatcher.add_handler(CommandHandler(event, function, pass_args=pass_args));

	def botSendMessage(self, msg):	self.__bot.sendMessage(chat_id=self.__botCid, text=msg);
	def botReplyMessage(self, msg):	self.__updater.message.reply_text(msg);

	def botCmdSecure(self, update):
		logger.debug(update.message.from_user.id in self.__masterList);
		if(not self.__masterList or update.message.from_user.id in self.__masterList):	return True;
		else:	return False;
# TELEGRAM BOT ASSIST CLASS #

# TIMMER`S FUNCTION #
def THRTIME_monitoringCPU():
	monitor = cMonitor();
	try:	del logmon.rateCPU[0];
	except:	pass;
	logmon.rateCPU.append(monitor.using_cpurate());

	if(logmon.rateCPU[-1] >= args.overheatcpu or abs(logmon.rateCPU[-1]-logmon.rateCPU[-2]) >= args.diffcpu):
		logger.warning("  Change in CPU usage is {}%".format(logmon.rateCPU[-1] - logmon.rateCPU[-2]));
		tele.botSendMessage("*CPU usage is {}%.".format(logmon.rateCPU[-1]));
		pass;

	monThread.append(threading.Timer((args.termonitor * 60), THRTIME_monitoringCPU));
	monThread[-1].start();

def THRTIME_monitoringMEM():
	monitor = cMonitor();
	try:	del logmon.rateMEM[0];
	except:	pass;
	logmon.rateMEM.append(monitor.using_cpurate());

	if(logmon.rateMEM[-1] >= args.overheatmem or abs(logmon.rateMEM[-1]-logmon.rateMEM[-2]) >= args.diffmem):
		logger.warning("  Change in MEMORY usage is {}%".format(logmon.rateMEM[-1] - logmon.rateMEM[-2]));
		tele.botSendMessage("*Memory usage is {}%.".format(logmon.rateMEM[-1]));
		pass;

	monThread.append(threading.Timer((args.termonitor * 60), THRTIME_monitoringMEM));
	monThread[-1].start();
# TIMMER`S FUNCTION #

def TEST():
	jb = tele.getJob();
	jb.start();
	logger.info(jb.jobs());
	monThread.append(threading.Timer(10, TEST));
	monThread[-1].start();

def terminate(signum, frame):
	for t in monThread:
		if(t.is_alive()):	t.cancel();
	del logmon;
	del tele;
	logger.info("Receive Signal {0}.".format(signum));
	logger.info("Terminating...");
	sys.exit(signum);
	pass;

def main():
	#---------- Global ----------#
	global tele;
	global logmon;
	global monThread;
	#---------- Global ----------#

	monThread = [];

	tele = cTelegramBot(key=args.teltoken, masters=args.mastertoken, cid=args.chattoken);

	#signal.signal(signal.SIGINT, terminate);
	#signal.signal(signal.SIGTERM, terminate);

	if(args.termonitor > 0):
		logmon = cLogMonitor();
		THRTIME_monitoringCPU();
		THRTIME_monitoringMEM();
		TEST();
		pass;

	## MONITORING COMMNAD ##
	logger.debug("  * Set event handler.");

	try:
		tele.setUpdaterEvent("help",			onCommandHelp);
	except Exception as e:	logger.debug(e);
	'''
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
	'''

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
	parser.add_argument('--log_path', dest='logpath', type=str, default="/var/log/teleMonitor/", help="Log Path. [Default:/var/log/teleMonitor/]");
	parser.add_argument('--location_this', dest='locationthis', action='store_false', default=True, help="Develop only");


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
	logger = logging.getLogger("TeleMonitor");
	try:
		if(not os.path.exists(os.path.abspath(args.logpath))):	os.makedirs(os.path.abspath(args.logpath));
		lHandler = logging.handlers.TimedRotatingFileHandler(filename=os.path.join(os.path.abspath(args.logpath), "teleMonitor.logs"), when='midnight', interval=1, encoding='utf-8');
		lHandler.suffix = "log-%Y%m%d";
	except:
		lHandler = logging.FileHandler("teleMonitor.logs");
	lHandler.setFormatter(logging.Formatter("[%(process)d] [%(levelname)s] [%(asctime)s]\t%(message)s"));
	logger.addHandler(lHandler);
	logger.setLevel(logging.DEBUG);
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
		if(args.locationthis):
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
				logger.info("Run daemon using 'systemctl start teleMonitor.service' command.");
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