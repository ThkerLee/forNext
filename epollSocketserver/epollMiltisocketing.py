import socket,select,struct,hashlib
from websocketcontentcode import websocketContentcode
from websocketprocessor import websocketProcessor
class epollServer():
	global	md5
	md5=hashlib.md5
	def __init__(self,argv):
		global md5
		self.name=argv['servername']
		self.serveradd=argv['serveradd']
                self.serverport=argv['serverport']
     	        self.processor=argv['processor']
		self.clientcon=dict()
		self.clientadd=dict()
		self.handed=list()
		self.request=dict()
	def run(self):
		global md5
		tmplist=list()
		print '		............... Server Will Running  ...........\n'
		serverfd=md5(self.name).hexdigest()
		serverfd=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		serverfd.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		serverfd.setblocking(0)
		print '............... SocketServer %s is Starting         ...........' % self.name
		print '............... SockteServer %s ID is %s            ...........' % (self.name,md5(self.name).hexdigest())
		serverfd.bind((self.serveradd,self.serverport))
		serverfd.listen(1)
		print '............... SocktServer %s is Started          ...........' % self.name
		epollfd=select.epoll()
		epollfd.register(serverfd.fileno(),select.EPOLLIN)
		print '............... EpollServer for %s is Started ...........\n\n' % (self.name) 

	
		while(True):
			even=epollfd.poll(1)	
			if len(even)>0:
				for confd,event in even:
					if confd ==serverfd.fileno():
						if confd not in self.clientcon:
							newconfd,newadd=serverfd.accept()
							self.clientcon[newconfd.fileno()]=newconfd
							self.clientadd[newconfd.fileno()]=newadd[0]
							newconfd.setblocking(0)
							epollfd.register(newconfd.fileno(),select.EPOLLIN)
							print '............ New Client Session From %s  ............' %newadd[0]
					else:
						if event & select.EPOLLIN:
							if confd not in self.handed:
								msg=self.recvmsg(self.name,confd)
								response=self.processor.hand(self.name,confd,msg)
								if self.sendmsg(self.name,confd,response):
									self.handed.append(confd)
									print '............ Client %s Is Hand OK ............' %self.clientadd[confd]	
									epollfd.modify(confd,select.EPOLLIN)
							else:
								msg=self.recvmsg(self.name,confd)
								print '%s' %msg
								if msg :
									request=self.processor.epollin(msg)
									self.request[confd]=request
									epollfd.modify(confd,select.EPOLLOUT)
								else:
									epollfd.modify(confd,select.EPOLLHUP)			
						elif event & select.EPOLLOUT:
							if confd in self.request :
								msg=self.request[confd]
								response=self.processor.epollout(msg)
								if self.sendmsg(self.name,confd,response):
									epollfd.modify(confd,select.EPOLLIN)
								
						elif event & select.EPOLLHUP:
							epollfd.unregister(confd)
                                                	self.clientcon[confd].close()
                                                	self.handed.remove(confd)

	def sendmsg(self,servername,confd,sendcontent):
		if sendcontent<0:
			return False
		else:
			print 'fasong %s' %servername
			self.clientcon[confd].send(sendcontent)
			return True	
	def recvmsg(self,servername,confd,SIZE=4096):
		print 'shoudao  %s' %servername
		recvedcontent=self.clientcon[confd].recv(SIZE)
		return recvedcontent


if __name__=='__main__':
	contentcode=websocketContentcode()
	pro=websocketProcessor()
	serverlist={'servername':'ftp','serveradd':'0.0.0.0','serverport':8000,'processor':pro}
        server=epollServer(serverlist)
        server.run()
