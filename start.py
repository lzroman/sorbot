from sorbot import *

bot = sorbot(conf['token'], conf['chat_id'], conf['botname'], conf['admin_ids'])
bot.plugins_add(jirniy)
bot.plugins_add(pomyanem)
bot.plugins_add(ban_new_user)
bot.plugins_add(ruletka)
bot.plugins_add(sorbetoban)
bot.plugins_add(achievements_list)
bot.plugins_add(stickers)
bot.plugins_add(when_join)
bot.plugins_add(quotes)
#bot.plugins_add(bassboost)
bot.plugins_add(voicetomusic)
#bot.plugins_add(wmark)
bot.plugins_add(showhelp)
bot.plugins_add(daily_pidor)
bot.start()
