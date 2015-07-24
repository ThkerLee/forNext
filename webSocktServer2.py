import socket,select,struct,hashlib
import base64
class websocketserver():
	def __init__(self,serverAdd='0.0.0.0',serverPort=8080):
		self.serverfd=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.serverfd.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		self.serverfd.setblocking(0)
		self.serverAdd=serverAdd
		self.serverPort=serverPort
		self.curCons={}
		self.hashand=[]

	def run(self):
		print '       Server is starting ......'
		self.serverfd.bind((self.serverAdd,self.serverPort))
		self.serverfd.listen(1)
		print '       Socket is OK on Port:%d' % (self.serverPort)
		epoll=select.epoll()
		
                epoll.register(self.serverfd.fileno(),select.EPOLLIN)
		print '       Epoll is ON '
		print '       Server started on %s:%d' % ( self.serverAdd,self.serverPort)
		print 'Epoll server fd is %s' % self.serverfd.fileno()
		while (True):
			events=epoll.poll(1)
			print 'Waiting Connect...........'
			for fd ,event in events:
				if fd == self.serverfd.fileno():
					if fd  not in self.curCons:
						try:
							clientfd,clientadd=self.serverfd.accept()
							self.curCons[clientfd.fileno()]=clientfd
							print 'New socket Fd is: %s,Address is :%s' % (clientfd.fileno(),clientadd[0])
							clientfd.setblocking(0)
							epoll.register(clientfd.fileno(),select.EPOLLIN)
						except socket.error:
							pass
				else:	
					if event & select.EPOLLIN:
						if fd not in self.hashand:
							if self.handshake(fd):
								self.hashand.append(fd)
                                              			print 'New socket Fd  %s is Handed' % clientfd.fileno()
						else:
							recvcontent=self.recvmeassage(fd)
							if recvcontent :
								if  'get' in recvcontent:
									epoll.modify(fd,select.EPOLLOUT)
							else:
								epoll.modify(fd,select.EPOLLHUP)
					elif event & select.EPOLLOUT:
						responcontent="hello"
						self.sendmessage(fd,responcontent)
						epoll.modify(fd,select.EPOLLIN)
					elif event & select.EPOLLHUP:

						epoll.unregister(fd)
						self.curCons[fd].close()
						del self.curCons[fd]
					
	def handshake(self,fileno):
		msg=self.curCons[fileno].recv(1024)
		key=''
		headers={}
                if not len(msg):
                        return False
		header,data=msg.split('\r\n\r\n',1)
                for line in header.split('\r\n')[1:]:
			key,value=line.split(': ',1)
			headers[key]=value
                        if headers.has_key('Sec-WebSocket-Key'):
                                key = base64.b64encode(hashlib.sha1(headers['Sec-WebSocket-Key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
                        if not key:
                                self.curCons[fileno].close()
                                return False
                response = 'HTTP/1.1 101 Switching Protocols\r\n'\
                        'Upgrade: websocket\r\n'\
                        'Connection: Upgrade\r\n'\
                        'Sec-WebSocket-Accept:' + key + '\r\n\r\n'
                self.curCons[fileno].send(response)
                return True
	
	
	def sendmessage(self,fileno,data):
		head='\x81'
		if len(data) <126:
			head+=struct.pack('B',len(data))
		elif len(data) <=0xFFFF:
			head+=struct.pack('!BH',126,len(data))
		else:
			head+=struct.pack('!BQ',127,len(data))
		self.curCons[fileno].send(head+data)	
		return True

	def recvmeassage(self,fileno,size=8192):
		data=self.curCons[fileno].recv(size)
		
		if not data:
			return False
		length=ord(data[1]) & 127
		if length == 126:
			mask=data[4:8]
			raw=data[8:]
		elif length == 127:
            		mask = data[10:14]
         	   	raw = data[14:]
        	else:
            		mask = data[2:6]
            		raw = data[6:]
		content=' '
		for vaule,data in enumerate(raw):
			content+=chr(ord(data) ^ ord(mask[vaule%4]))
		return content

if __name__=='__main__':
	server=websocketserver()
	server.run()


