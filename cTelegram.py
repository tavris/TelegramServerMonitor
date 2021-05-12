import telegram;
from telegram.ext import Updater, CommandHandler, CallbackContext;

class cTelegram:
	__bot = None;
	__updater = None;

	def __init__(self, key, masters=None, cid=None):
		self.__bot = cTelegramBot(key, masters, cid);
		self.__updater = cTelegramUpdater(key, self.__bot.getBot(), cid);
		pass;

	def __del__(self):
		del self.__bot;
		del self.__updater;
		pass;

	def botCmdSecure(self, update):
		#logger.debug(update.message.from_user.id in self.__masterList);
		if(not self.__masterList or update.message.from_user.id in self.__masterList):	return True;
		else:	return False;

	def getBotClass(self):	return self.__bot;
	def getUpdaterClass(self):	return self.__updater;

	# Trampoline #
	def sendMessage(self, msg):	self.__bot.botSendMessage(msg);
	def replyMessage(self, msg):	self.__updater.replyMessage(msg);

	def addCommand(self, command, handle, pars_args=False):	self.__updater.addCommandHandler(command, handle, pars_args);
	def start_polling(self):	self.__updater.start();
	# Trampoline #

# TELEGRAM BOT ASSIST CLASS #
class cTelegramBot:
	__bot = None;
	__botCid = None;
	__masterList = [];

	def __init__(self, key, masters=None, cid=None):
		try:
			self.__bot = telegram.Bot(token=key);
			self.__masterList = masters;

			if(cid is not None):	self.__botCid = cid;
			else:	self.__botCid = self.__bot.getUpdates()[-1].message.chat.id;
		except Exception as e:	pass;
		pass;

	def __del__(self):
		try:
			pass;
		except Exception as e:	pass;
		pass;

	def getBot(self):	return self.__bot;
	def botSendMessage(self, msg):	self.__bot.sendMessage(chat_id=self.__botCid, text=msg);

class cTelegramUpdater:
	__updater = None;
	__cid = None;

	def __init__(self, key, bot, cid=None):
		try:
			self.__updater = Updater(token=key);

			if(cid is not None):	self.__cid = cid;
			else:	self.__cid = bot.getUpdates()[-1].message.chat.id;
		except Exception as e:	self.__updater = e;
		pass;

	def __del__(self):
		del self.__updater;
		del self.__cid;
		pass;

	def getUpdater(self):	return self.__updater;
	def replyMessage(self, msg):	self.__updater.message.reply_text(msg);
	def	addCommandHandler(self, command, handle, pass_args=False):	self.__updater.dispatcher.add_handler(CommandHandler(command, handle, pass_args=pass_args));
	def start(self):
		self.__updater.start_polling();
		#self.__updater.idle();
# TELEGRAM BOT ASSIST CLASS #