import telegram, os;
from telegram.ext import Updater, CommandHandler, CallbackContext;
from cMonitor import cMonitor;

# TELEGRAM-BOT COMMAND EVENT HANDLER #
## HELP COMMAND CALLBACK ##
def onCommandHelp(update: telegram.Update, _: CallbackContext) -> None:
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
	monitor = cMonitor();
	mInfo = monitor.cpu_info();

	msg  = "* CPU INFO\n";
	msg += "   - Physical Core : %d\n" % mInfo['pCore'];
	msg += "   - Logical Core : %d\n" % mInfo['lCore'];
	msg += "   - CPU Frequency : {} GHz\n".format( round(mInfo['freq'][0]/1024, 1) );
	update.message.reply_text(msg);

def onCommandCPUUse(update: telegram.Update, _: CallbackContext) -> None:
	monitor = cMonitor();
	mInfo = monitor.using_cpu_info();

	msg  = "* CPU USE\n";
	msg += "   - User	: {}%\n".format( mInfo[0] );
	msg += "   - System	: {}%\n".format( mInfo[2] );
	msg += "   - idle	: {}%\n".format( mInfo[3] );
	update.message.reply_text(msg);

def onCommandMemoryInfo(update: telegram.Update, _: CallbackContext) -> None:
	monitor = cMonitor();
	mInfo = monitor.using_mem_info();

	msg  = "* MEMORY USE\n";
	msg += "   - [Physical]	Total : %4.1fG, Used : %4.1fG, Free : %4.1fG, Avaliable : %4.1fG\n" % (mInfo['physical'][0]/1024**3, mInfo['physical'][3]/1024**3, mInfo['physical'][4]/1024**3, mInfo['physical'][1]/1024**3);
	msg += "   - [Swap]		Total : %4.1fG, Used : %4.1fG, Free : %4.1fG\n" % (mInfo['swap'][0]/1024**3, mInfo['swap'][1]/1024**3, mInfo['swap'][2]/1024**3);
	update.message.reply_text(msg);

def onCommandNetInfo(update: telegram.Update, _: CallbackContext) -> None:
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
	monitor = cMonitor();
	mInfo = monitor.detail_net_info();

	msg  = "* NETWORK DETAIL\n";
	msg += "%5s %10s %17s:%5s %10s\n" % ("pid", "name", "IP", "port", "status");
	for k in mInfo.keys():
		msg += "%5d %10s %17s:%d %10s" % (k, mInfo[k]['name'], mInfo[k]['raddr'][0], mInfo[k]['raddr'][1], mInfo[k]['status']);
	update.message.reply_text(msg);

def onCommandTemperature(update: telegram.Update, _: CallbackContext) -> None:
	monitor = cMonitor();
	mInfo = monitor.temperature_info();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* TEMPERATURE\n";

	update.message.reply_text(msg);

def onCommandFans(update: telegram.Update, _: CallbackContext) -> None:
	monitor = cMonitor();
	mInfo = monitor.fans_info();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* FAN DETAIL\n";

	update.message.reply_text(msg);

def onCommandBattery(update: telegram.Update, _: CallbackContext) -> None:
	monitor = cMonitor();
	mInfo = monitor.battery_info();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* BATTERY DETAIL\n";

	update.message.reply_text(msg);

def onCommandBoottime(update: telegram.Update, _: CallbackContext) -> None:
	monitor = cMonitor();
	mInfo = monitor.boot_time();

	if(not mInfo):	msg = "This function is not available in the current environment.";
	else:
		msg  = "* BOOT TIME\n";
		msg += "   - {}".format(mInfo);

	update.message.reply_text(msg);

def onCommandConnectedUsers(update: telegram.Update, _: CallbackContext) -> None:
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

def onCommandClearMemory(update: telegram.Update, _: CallbackContext) -> None:
        os.system("echo 3 > /proc/sys/vm/drop_caches");
        os.system("sync")
        meg = "* Memory clear.";
        update.message.reply_text(msg);


# TELEGRAM-BOT COMMAND EVENT HANDLER #
