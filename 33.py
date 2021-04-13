import base64
import hashlib
from hashlib import sha512
from hashlib import sha256
from hashlib import sha1
#给password加密
h = "蓝色的樱桃丸子"

s1 = sha1()  #创建sha1加密对象
s1.update(h.encode("utf-8"))   #转码（字节流）
print(s1.hexdigest())


s256 = sha256()  #创建sha1加密对象
s256.update(h.encode("utf-8"))   #转码（字节流）
print(s256.hexdigest())


s512 = sha512()  #创建sha1加密对象
s512.update(h.encode("utf-8"))   #转码（字节流）
print(s512.hexdigest())


s = base64.b64encode(h.encode('utf-8'))
print(h)

m = hashlib.md5()
m.update(h.encode('utf-8'))
print(m.hexdigest())


