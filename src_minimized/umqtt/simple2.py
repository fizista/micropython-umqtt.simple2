import usocket as socket
from utime import ticks_add,ticks_ms,ticks_diff
class MQTTException(Exception):0
def pid_gen(pid=0):
	A=pid
	while True:A=A+1 if A<65535 else 1;yield A
class MQTTClient:
	def __init__(A,client_id,server,port=0,user=None,password=None,keepalive=0,ssl=False,ssl_params=None,socket_timeout=1,message_timeout=5):
		C=ssl_params;B=port
		if B==0:B=8883 if ssl else 1883
		A.client_id=client_id;A.sock=None;A.server=server;A.port=B;A.ssl=ssl;A.ssl_params=C if C else{};A.newpid=pid_gen()
		if not getattr(A,'cb',None):A.cb=None
		if not getattr(A,'cbstat',None):A.cbstat=lambda p,s:None
		A.user=user;A.pswd=password;A.keepalive=keepalive;A.lw_topic=None;A.lw_msg=None;A.lw_qos=0;A.lw_retain=False;A.rcv_pids={};A.last_ping=ticks_ms();A.last_cpacket=ticks_ms();A.socket_timeout=socket_timeout;A.message_timeout=message_timeout
	def _read(B,n):
		A=B.sock.read(n)
		if A==b'':raise MQTTException(1)
		if A is not None:
			if len(A)!=n:raise MQTTException(2)
		return A
	def _write(D,bytes_wr,length=-1):
		C=bytes_wr;A=length;B=D.sock.write(C,A)
		if A<0:
			if B!=len(C):raise MQTTException(3)
		elif B!=A:raise MQTTException(3)
		return B
	def _send_str(A,s):assert len(s)<65536;A._write(len(s).to_bytes(2,'big'));A._write(s)
	def _recv_len(D):
		A=0;B=0
		while 1:
			C=D._read(1)[0];A|=(C&127)<<B
			if not C&128:return A
			B+=7
	def _varlen_encode(C,value,buf,offset=0):
		B=offset;A=value;assert A<268435456
		while A>127:buf[B]=A&127|128;A>>=7;B+=1
		buf[B]=A;return B+1
	def _sock_timeout(A,socket_timeout=-1):
		B=socket_timeout
		if A.sock:A.sock.settimeout(A.socket_timeout if B<0 else B)
		else:raise MQTTException(28)
	def set_callback(A,f):A.cb=f
	def set_callback_status(A,f):A.cbstat=f
	def set_last_will(A,topic,msg,retain=False,qos=0):B=topic;assert 0<=qos<=2;assert B;A.lw_topic=B;A.lw_msg=msg;A.lw_qos=qos;A.lw_retain=retain
	def connect(A,clean_session=True,socket_timeout=-1):
		E=clean_session;A.sock=socket.socket();G=socket.getaddrinfo(A.server,A.port)[0][-1];A.sock.connect(G);A._sock_timeout(socket_timeout)
		if A.ssl:import ussl;A.sock=ussl.wrap_socket(A.sock,**A.ssl_params)
		F=bytearray(b'\x10\x00\x00\x00\x00\x00');B=bytearray(b'\x00\x04MQTT\x04\x00\x00\x00');D=10+2+len(A.client_id);B[7]=bool(E)<<1
		if bool(E):A.rcv_pids.clear()
		if A.user is not None:
			D+=2+len(A.user);B[7]|=1<<7
			if A.pswd is not None:D+=2+len(A.pswd);B[7]|=1<<6
		if A.keepalive:assert A.keepalive<65536;B[8]|=A.keepalive>>8;B[9]|=A.keepalive&255
		if A.lw_topic:D+=2+len(A.lw_topic)+2+len(A.lw_msg);B[7]|=4|(A.lw_qos&1)<<3|(A.lw_qos&2)<<3;B[7]|=A.lw_retain<<5
		H=A._varlen_encode(D,F,1);A._write(F,H);A._write(B);A._send_str(A.client_id)
		if A.lw_topic:A._send_str(A.lw_topic);A._send_str(A.lw_msg)
		if A.user is not None:
			A._send_str(A.user)
			if A.pswd is not None:A._send_str(A.pswd)
		C=A._read(4)
		if not(C[0]==32 and C[1]==2):raise MQTTException(29)
		if C[3]!=0:
			if 1<=C[3]<=5:raise MQTTException(20+C[3])
			else:raise MQTTException(20,C[3])
		A.last_cpacket=ticks_ms();return C[2]&1
	def disconnect(A,socket_timeout=-1):A._sock_timeout(socket_timeout);A._write(b'\xe0\x00');A.sock.close()
	def ping(A,socket_timeout=-1):A._sock_timeout(socket_timeout);A._write(b'\xc0\x00');A.last_ping=ticks_ms()
	def publish(A,topic,msg,retain=False,qos=0,dup=False,socket_timeout=-1):
		E=topic;B=qos;A._sock_timeout(socket_timeout);assert B in(0,1);C=bytearray(b'0\x00\x00\x00\x00');C[0]|=B<<1|retain|int(dup)<<3;F=2+len(E)+len(msg)
		if B>0:F+=2
		G=A._varlen_encode(F,C,1);A._write(C,G);A._send_str(E)
		if B>0:D=next(A.newpid);A._write(D.to_bytes(2,'big'))
		A._write(msg)
		if B>0:A.rcv_pids[D]=ticks_add(ticks_ms(),A.message_timeout*1000);return D
	def subscribe(A,topic,qos=0,socket_timeout=-1):E=topic;assert qos in(0,1);A._sock_timeout(socket_timeout);assert A.cb is not None,'Subscribe callback is not set';B=bytearray(b'\x82\x00\x00\x00\x00\x00\x00');C=next(A.newpid);F=2+2+len(E)+1;D=A._varlen_encode(F,B,1);B[D:D+2]=C.to_bytes(2,'big');A._write(B,D+2);A._send_str(E);A._write(qos.to_bytes(1,'little'));A.rcv_pids[C]=ticks_add(ticks_ms(),A.message_timeout*1000);return C
	def _message_timeout(A):
		C=ticks_ms()
		for (B,D) in A.rcv_pids.items():
			if ticks_diff(D,C)<=0:A.rcv_pids.pop(B);A.cbstat(B,0)
	def wait_msg(A,socket_timeout=None):
		if A.sock:G=A._read(1)
		else:raise MQTTException(28)
		A.sock.settimeout(socket_timeout)
		if G is None:A._message_timeout();return None
		if G==b'\xd0':
			if A._read(1)[0]!=0:MQTTException(-1)
			A.last_cpacket=ticks_ms();return
		B=G[0]
		if B==64:
			D=A._read(1)
			if D!=b'\x02':raise MQTTException(-1)
			F=int.from_bytes(A._read(2),'big')
			if F in A.rcv_pids:A.last_cpacket=ticks_ms();A.rcv_pids.pop(F);A.cbstat(F,1)
			else:A.cbstat(F,2)
		if B==144:
			C=A._read(4)
			if C[0]!=3:raise MQTTException(40,C)
			if C[3]==128:raise MQTTException(44)
			if C[3]not in(0,1,2):raise MQTTException(40,C)
			E=C[2]|C[1]<<8
			if E in A.rcv_pids:A.last_cpacket=ticks_ms();A.rcv_pids.pop(E);A.cbstat(E,1)
			else:raise MQTTException(5)
		A._message_timeout()
		if B&240!=48:return B
		D=A._recv_len();H=int.from_bytes(A._read(2),'big');I=A._read(H);D-=H+2
		if B&6:E=int.from_bytes(A.sock.read(2),'big');D-=2
		J=A._read(D);K=B&1;L=B&8;A.cb(I,J,bool(K),bool(L));A.last_cpacket=ticks_ms()
		if B&6==2:A._write(b'@\x02');A._write(E.to_bytes(2,'big'))
		elif B&6==4:raise NotImplementedError()
		elif B&6==6:raise MQTTException(-1)
	def check_msg(A):A._sock_timeout(0);return A.wait_msg(socket_timeout=A.socket_timeout)