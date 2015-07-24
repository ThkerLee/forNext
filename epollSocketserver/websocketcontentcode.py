import struct
from classBase  import contentcode
class websocketContentcode(contentcode):
	def encode(self,encontent):
		head='\x81'
                if len(encontent) <126:
                        head+=struct.pack('B',len(encontent))
                elif len(encontent) <=0xFFFF:
                        head+=struct.pack('!BH',126,len(encontent))
                else:
                        head+=struct.pack('!BQ',127,len(encontent))
                recontent=head+encontent
		return recontent
	def uncode(self,uncontent):
		if not uncontent:
                        return False
                length=ord(uncontent[1]) & 127
                if length == 126:
                        mask=uncontent[4:8]
                        raw=uncontent[8:]
                elif length == 127:
                        mask = uncontent[10:14]
                        raw = uncontent[14:]
                else:
                        mask = uncontent[2:6]
                        raw = uncontent[6:]
                recontent=' '
                for vaule,data in enumerate(raw):
                        recontent+=chr(ord(data) ^ ord(mask[vaule%4]))
                return recontent
