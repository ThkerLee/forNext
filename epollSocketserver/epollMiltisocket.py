import socket,select,struct,hashlib
class epollServer():
	global	md5
	md5=hashlib.md5
	def __init__(self,argv):
		self.name=list()
                self.serverfd=dict()
		self.epollfd=dict()
		self.clientcon=dict()
                self.serveradd=dict()
                self.serverport=dict()	
		self.events=dict()
		self.handed=dict()
		runkey={'tuple':self.init_tupleDict,'dict':self.init_dict}
		if type(argv)== tuple:
			runtype='tuple'
		if type(argv)== dict:
			runtype='dict'
		runkey.get(runtype)(argv)	
	def init_tupleDict(self,listdict):
		for line in listdict:
			self.name.append(line['servername'])
			self.serveradd[line['servername']]=line['serveradd']
			self.serverport[line['servername']]=line['serverport']

	def init_dict(self,dic):
		self.name.append(dic['servername'])
                self.serveradd[dic['servername']]=line['serveradd']
                self.serverport[dic['servername']]=line['serverport']	
	def run(self):
		tmplist=list()
		servernum=len(self.name)
		print '		............... Have %s Server Will Running  ...........\n' % servernum
		global md5
		for servername in self.name:
			self.clientcon[servername]=dict()
			self.handed[servername]=list()
			serverid=md5(servername).hexdigest()
			serverid=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			serverid.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			serverid.setblocking(0)
			self.serverfd[servername]=serverid
			print '............... SocktServer %s is Starting         ...........' % servername
			print '............... SocktServer %s ID is %s            ...........' % (servername,md5(servername).hexdigest())
			serverid.bind((self.serveradd[servername],self.serverport[servername]))
			serverid.listen(20)
			print '............... SocktServer %s is Started          ...........' % servername
			epollid='%s%s' %('epollid',serverid)
			epollid=select.epoll()
			self.epollfd[servername]=epollid
			epollid.register(serverid.fileno(),select.EPOLLIN)
			print '............... EpollServer for %s is Started ...........\n\n' % (servername) 

	
		while(True):
			for servername in self.name:
				even=self.epollfd[servername].poll(1)	
				if len(even)>0:
					print '%s' %even	
					self.events[servername]=even
					print '%s %s' % (servername ,self.events)
					for confd,event in self.events[servername]:
						if confd ==self.serverfd[servername].fileno():
							if confd not in self.clientcon[servername]:
								newconfd,newadd=self.serverfd[servername].accept()
								self.clientcon[servername][newconfd.fileno()]=newconfd
								newconfd.setblocking(0)
								self.epollfd[servername].register(newconfd.fileno(),select.EPOLLIN)
						else:
							if event & select.EPOLLIN:
								print '%s' % self.clientcon[servername][confd].fileno() 
								if confd not in self.handed[servername]:
									pass
								else:
									pass
						
							elif event & select.EPOLLOUT:
								pass
	
							elif event & select.EPOLLHUP:
								self.epollfd[servername].unregister(confd)
                                                		self.self.clientcon[servername][confd].fileno().close()
                                                		self.handed[servername].remove(confd)
									
								


if __name__=='__main__':
	serverlist=({'servername':'epoo','serveradd':"0.0.0.0",'serverport':8989}
		   ,{'servername':'ftp','serveradd':'0.0.0.0','serverport':8000})
        server=epollServer(serverlist)
        server.run()
