import os
import smtplib
import getpass
import random
import time
import telepot

username = input("enter username:")  # 'ntuscbot@gmail.com'
password = getpass.getpass("Please input domain password: ")
server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
server.ehlo()
server.login(username, password)


class person:
    def __init__(self, uid, rid):
        self.uid = uid
        self.rid = rid
        self.votes = 0


chairman = ''  # chairman's ID
registered = []
registered_uid = []
queue = []
idlist = []  # some ID, such as 'B01234567'


def register(uid, rid):
    if rid in idlist:
        # generate code
        rcode = ''.join(random.choice("012345678") for i in range(5))
        found = 0
        for i in queue:
            if i[0] == uid:
                i[1] = rcode
                found = 1
        if not found:
            queue.append([uid, rcode, rid])

        # send code to ntumail
        fromaddr = username
        receiver = '{}@ntu.edu.tw'.format(rid)
        message = """
        From: {sender}
        To: {receiver}
        Subject: NTUSC_vote_system

        {content}
        """.format(
            sender=username,
            receiver=receiver,
            content=rcode
        )
        print(fromaddr)
        print(receiver)
        print(message)
        server.sendmail(fromaddr, receiver, message)

    else:
        bot.sendMessage(uid, "請輸入學代學號 ex:B01234567")


def verify(uid, rid, code):
    for i in queue:
        if i[0] == uid:
            if i[1] == code:
                registered.append(person(uid, rid))
                registered_uid.append(uid)
                bot.sendMessage(uid, "成功登入")
            else:
                bot.sendMessage(uid, "驗證碼錯誤")
            return
    bot.sendMessage(uid, "尚未註冊")


def vote(uid, number):
    for i in registered:
        if i.uid == uid:
            i.votes = number


def default_answer(uid):
    bot.sendMessage(uid, "/login 學號\n/code 學號 驗證碼")


def default_vote(uid):
    bot.sendMessage(uid, "/vote 號碼")


def newroll(uid, context):
    for i in registered:
        if i.uid == uid:
            if i.rid == chairman:
                for j in registered:
                    j.votes = '0'
                    bot.sendMessage(j.uid, context)
            else:
                default_vote(uid)


def endroll(uid):
    for i in registered:
        if i.uid == uid:
            if i.rid == chairman:
                result = ''
                for j in registered:
                    result += "{} {}\n".format(j.rid, j.votes)
                bot.sendMessage(uid, result)
            else:
                default_vote(uid)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        text = msg['text'].split(" ")

        command = text[0]
        if chat_id not in registered_uid:
            if command == "/login":
                register(chat_id, text[1])
            elif command == "/code":
                verify(chat_id, text[1], text[2])
            else:
                default_answer(chat_id)
        else:
            if command == "/vote":
                vote(chat_id, text[1])
            elif command == "/new":
                newroll(chat_id, text[1])
            elif command == "/end":
                endroll(chat_id)
            else:
                default_vote(chat_id)


TOKEN = os.environ.get('NTUSC_BOT_TOKEN', '')

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print('Listening ...')
# server.quit()
while 1:
    time.sleep(10)
