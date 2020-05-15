import smtplib
import time
import threading
import random
import sys

random.seed(time.time())

providers = {
	"att" : "@mms.att.net",
	"verizon" : "@vzwpix.com",
	"tmobile" : "@tmomail.net",
	"sprint" : "@pm.sprint.com",
	"virgin" : "@vmpix.com",
	"cricket" : "@mms.cricketwireless.net",
	"boost" : "@myboostmobile.com",
	"email" : ""
}

# Requires running server in the same directory as a text file of insults (one per line)
insults = []
with open("Insults.txt") as f:
	insults = f.readlines()
	for i, line in enumerate(insults):
		insults[i] = '\n'.join(line.split('\\'))


# Used for managing people to send texts to
class client(threading.Thread):

	# string (Eric, Lisa, etc), string (att, verizon, email, etc), string (phone number or email address), int (how often, in hours), float (last message time)
	def __init__(self, name, provider, address, frequency, lastmessagetime):
		
		threading.Thread.__init__(self)

		if provider not in providers:
			print("Provider not supported")
			return
		
		self.name = name
		self.provider = provider
		self.addrnum = address
		self.address = address + providers[provider]
		
		if frequency < 1:
			self.frequency = 168
		else:
			self.frequency = frequency
		
		temp = "From: Lloyd's Mockerybot\n"
		temp += "To: " + name + " <" + self.address + ">\n"
		if provider == "email":
			temp += "Subject: An Affront Just for You!\n\n"
		self.template = temp
		
		self.active = True

		self.lastmessagetime = lastmessagetime


	# Sends an insult to send to the client using Google's SMTP server
	def send_message(self, insult):
		message = self.template
		message += "Oi, " + self.name + "!\n\n"
		message += insult + "\nDo one\n - Mockerybot"

		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.starttls()
		server.login('<youremail>', '<password>')
		server.sendmail("Lloyd's Mockerybot", self.address, message)
		server.quit()

		self.lastmessagetime = time.time()


	# Updates the user's last message sent time in client list.
	def update_in_file(self):

		filename = ""

		if len(sys.argv) == 2:
			filename = sys.argv[1]
		else:
			filename = "Clients.txt"

		lines = None

		with open(filename, "r") as f:
			found = False
			lines = f.readlines()
			
			for i, line in enumerate(lines):
				attr = line.split('-')
				if len(attr) != 5:
					continue
				if attr[0] == self.name:
					found = True
					attr[4] = str(time.time())
					lines[i] = '-'.join(attr) + '\n'
					break

			if not found:
				lines.append(self.name + '-' + self.provider + '-' + self.addrnum + '-' + str(self.frequency) + '-' + str(time.time()) + '\n')


		with open(filename, "w") as f:
			for line in lines:
				f.write(line)



	# Loop that sends message to clients at their given frequency
	def run(self):

		if self.lastmessagetime != None:
			nextmsgtime = self.lastmessagetime + (self.frequency * 3600) - 2
			if time.time() < nextmsgtime:
				time.sleep(nextmsgtime - time.time())

		while self.active:

			threadLock.acquire()

			insult = random.choice(insults)
			self.send_message(insult)
			print("\nMessage sent to " + self.name + " at " + time.ctime(time.time()))
			print("mockerybot-hub >> ", end="")

			self.update_in_file()

			threadLock.release()

			self.lastmessagetime = time.time()

			time.sleep((self.frequency * 3600) - 2)

			


# "Main method"
threadLock = threading.Lock()

clientlist = []

if len(sys.argv) == 2:
	clienttextfilename = sys.argv[1]
	with open(clienttextfilename) as file:
		lines = file.readlines()
		for line in lines:
			if line == '\n':
				continue
			attr = line.split('-')
			newc = client(attr[0], attr[1], attr[2], int(attr[3]), float(attr[4]))
			clientlist.append(newc)
			newc.start()



# Used for server operations, adding and removing clients, etc
cmd = [""]
while cmd[0] != "shutdown":

	cmd = input("mockerybot-hub >> ").split()

	if len(cmd) == 0:
		continue

	if cmd[0] == "clientlist":
		for c in clientlist:
			print(c.name + " - msg every " + str(c.frequency) + " hours - last message sent " + time.ctime(c.lastmessagetime))
		
	elif cmd[0] == "remove":
		for c in clientlist:
			if c.name == cmd[1]:
				c.active = False
				clientlist.remove(c)
				break
		
	elif cmd[0] == "addclient":
		threadLock.acquire()
		nm = input("Name: ")
		prov = input("Provider: ")
		addr = input("Address/number: ")
		freq = int(input("Frequency (hours): "))
		threadLock.release()
		newc = client(nm, prov, addr, freq, 0.0)
		clientlist.append(newc)
		newc.start()

	elif cmd[0] == "refresh":
		with open("Insults.txt") as f:
			insults = f.readlines()
			for i, line in enumerate(insults):
				insults[i] = '\n'.join(line.split('\\'))

	else:
		print("""  clientlist -- lists clients by name and frequency of invective
  remove <client name> -- removes a client from the insult list
  addclient -- prompts for items to add a client to the list
  refresh -- refreshes the list of messages from Insults.txt
  shutdown -- kills server
  help -- prints this message""")
