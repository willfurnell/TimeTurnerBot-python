#####################################################################################
# COPYRIGHT 2014 WILL FURNELL (http://github.com/willfurnell/TimeTurnerBot-python/) #
#####################################################################################

import socket
import configparser
import time
import json
import urllib.request
import urllib.error
import urllib.parse

# Get required information from the configuration file
config = configparser.ConfigParser()
config.sections()
config.read('config.ini')  # The configuration file containing all nessasary options.

# User information file
def loadfile():
    with open('user_tz.json') as data_file:
        user_tz = json.load(data_file)
        return user_tz

# Convert the output to a human readable message
def data_to_message(data):
    return data.split(":", 2)[2]

# Send a PING back to the server
def sendping(output):
    str_buff = "PONG " + output.split()[1] + '\r\n'
    irc.send(str_buff.encode())  # Returns 'PONG' back to the server (prevents pinging out!)


# !time command
def timecmd(channel, uinput):

    if uinput == "help":
        s(channel, "TimeBot Help. Use: !time <city> Contact will for further information.")
    elif uinput == "future" or uinput == "the future":
        s(channel, "I'm sorry " + user_nick + " I'm afraid I cannot do that!")
    elif uinput == "more":
        s(channel, "'What we need,' said Dumbledore slowly, and his light-blue eyes moved from Harry to Hermione, 'is more time'... 'Miss Granger, three turns should do it. Good luck.'")
    elif uinput == "past" or uinput == "the past":
        s(channel, "'The past is a construct of the mind. It blinds us. It fools us into believing it. But the heart wants to live in the present. Look there. You'll find your answer.'")
    elif uinput == "wiki" or uinput == "info":
        s(channel, "Wiki Page: http://wiki.awfulnet.org/w/TimeBot")
    elif uinput == "TimeBot" or uinput == "timebot" or uinput == "TimeTurnerBot" or uinput == "now":
        servertime = time.strftime('%Y-%m-%d %H:%M:%S')
        s(channel, "TimeTurnerBot Server Time: " + servertime)
    else:
        user = 0
        internaluser = uinput.lower()
        for u in user_tz:
            if internaluser in u:
                uinput = user_tz[internaluser]
                user = 1

        uinputweb = urllib.parse.quote_plus(uinput)
        url = "http://api.worldweatheronline.com/free/v1/tz.ashx?q=" + uinputweb + "&format=json&key=" + config['main']['apikey'] + ""
        apierror = 0
        try:
            apifile = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            s(channel, "API error! " + str(e))
            apierror = 1

        if apierror == 0:
            apijson = json.loads(apifile.read().decode('utf-8'))
            print(apijson)
            if "error" in apijson['data']:
                s(channel, "Error! The time could not be given for the city/person you requested!")
            elif user == 1:
                finaltime = time.strptime(apijson['data']['time_zone'][0]['localtime'], '%Y-%m-%d %H:%M')
                finaltime = time.strftime('%A %d %B %Y %H:%M', finaltime)
                s(channel, "The time where " + internaluser + " lives (" + uinput + ") is " + finaltime)
            else:
                finaltime = time.strptime(apijson['data']['time_zone'][0]['localtime'], '%Y-%m-%d %H:%M')
                finaltime = time.strftime('%A %d %B %Y %H:%M', finaltime)
                s(channel, "The time in " + uinput + " is " + finaltime)


# !addtz command
def addtzcmd(channel, uinput):
    if uinput == "help":
        s(channel, "TimeBot Help. Use: !time <city> Contact will for further information.")
    elif uinput == "future" or uinput == "the future":
        s(channel, "I'm sorry " + user_nick + " I'm afraid I cannot do that!")
    elif uinput == "now":
        s(channel, "Well done smartass, I actually need to know where you live though...")
    else:
        addition = {user_nick: uinput}
        user_tz.update(addition)
        with open('user_tz.json', 'w') as data_file:
            json.dump(user_tz, data_file, indent=4, sort_keys=True)
        s(channel, "Location added/updated")


# Function to send a message to the specified channel
def s(c, i):
    i = "PRIVMSG " + c + " :" + i + "\r\n"
    irc.send(i.encode())


user_tz = loadfile()

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Defines the socket
try:
    print("CONNECTING TO: " + config['main']['server'])
    irc.connect((config['main']['server'], 6667))  # Connects to the server
except:
    quit("ERROR connecting to " + config['main']['server'] + "! Bailing...")

output = irc.recv(4096)  # receive the text
output = output.decode('utf-8').strip()
# This is needed for the initial PING that is sent by the server
if "PING" in output:  # Check if sent text is PING
    sendping(output)

#Tell the server who you are
str_buff = "NICK " + config['main']['nick'] + "\r\n"
irc.send(str_buff.encode())  # Sets nick
str_buff = "USER " + config['main']['nick'] + " " + config['main']['nick'] + " " + config['main']['nick'] + " :TimeTurnerBot v0.1 (Python)!\r\n"
irc.send(str_buff.encode())  # Bot information

while 1:    # An infinite loop (the main program logic)
    output = irc.recv(4096)  # receive the text
    output = output.decode('utf-8').strip()
    print(output)
    splitout = output.split(" ")

    if "001" in output:
        str_buff = "PRIVMSG NICKSERV :IDENTIFY " + config['main']['nick'] + " " + config['main']['nickservpass'] + "\r\n"
        irc.send(str_buff.encode())  # Authenticate with NickServ
        str_buff = "JOIN " + config['main']['channels'] + "\r\n"
        irc.send(str_buff.encode())  # Join all specified channels
        str_buff = "UMODE2 +B\r\n"
        irc.send(str_buff.encode())

    if "PING" in output:  # Check if sent text is PING
        sendping(output)

    if "PRIVMSG" in output:
        user_nick = output.split('!')[0].split(":")[1]
        user_host = output.split('@')[1].split(' ')[0]
        user_message = data_to_message(output)

        channel = splitout[2]
        command = user_message.split()[0]


        if command == "!time":
            if len(user_message.split()) == 1:
                s(channel, "Error, city/person not defined!")
            else:
                uinput = user_message.replace(command, "").strip()
                timecmd(channel, uinput)

        if command == "!addtz":
            if len(user_message.split()) == 1:
                s(channel, "Error, city/person not defined!")
            else:
                uinput = user_message.replace(command, "").strip()
                addtzcmd(channel, uinput)

        if command == "!thelp":
            s(channel, "TimeBot Help:")
            s(channel, "Use !addtz <location> to add your location to TimeBot")
            s(channel, "Use !time <location/person> to see the time in <location> or where <person> lives.")


        if command == ">>>" and user_nick == "will" and user_host == config['main']['allowedhost']:
            if len(user_message.split()) == 1:
                s(channel, "Error!")
            else:
                uinput = user_message.replace(command, "")

                try:
                    output = str(eval(uinput))
                except SyntaxError as e:
                    output = "Syntax error: " + str(e)
                except TypeError as e:
                    output = "TypeError: " + str(e)

                s(channel, output)

        if command == "!ttbquit" and user_nick == "will" and user_host == config['main']['allowedhost']:
            s(channel, "Goodbye!")
            str_buff = "QUIT\r\n"
            irc.send(str_buff.encode())
            quit("User activated shutdown")

        if command == "!ttbpart" and user_nick == "will" and user_host == config['main']['allowedhost']:
            s(channel, "Goodbye!")
            str_buff = "PART " + channel + "\r\n"
            irc.send(str_buff.encode())

        if command == "!ttbjoin" and user_nick == "will" and user_host == config['main']['allowedhost']:
            if len(user_message.split()) == 1:
                s(channel, "Error, channel not defined!")
            else:
                uinput = user_message.replace(command, "").strip()
                str_buff = "JOIN " + uinput + "\r\n"
                s(channel, "Joined " + uinput)
