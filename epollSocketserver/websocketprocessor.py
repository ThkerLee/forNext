import base64
import hashlib
from classBase import processor
from websocketcontentcode import websocketContentcode
class websocketProcessor(processor):
	def hand(self,servername,confd,recvcontent):
                key=''
		response=''
                headers={}
                if not len(recvcontent):
                        return False
                header,data=recvcontent.split('\r\n\r\n',1)
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
                return response
	def verify():
                pass
	def epollin(self,recvcontent):
		contentcode=websocketContentcode()
		response=contentcode.uncode(recvcontent)
		return response
	def epollout(self,recvcontent):
		contentcode=websocketContentcode()
                response=contentcode.encode(recvcontent)
                return response
	def epollhup():
                pass
	
