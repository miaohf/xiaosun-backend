import base64
import json
from Crypto.Cipher import AES

class WXBizDataCrypt:
	def __init__(self, appId, sessionKey):
		self.appId = appId
		self.sessionKey = sessionKey

	def decrypt(self, encryptedData, iv):
		# base64 decode
		sessionKey = base64.b64decode(self.sessionKey)
		encryptedData = base64.b64decode(encryptedData)
		iv = base64.b64decode(iv)

		cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

		# print(cipher)

		# print('cipher.decrypt')
		# print(self._unpad(cipher.decrypt(encryptedData)))

		decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))
		# decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData).decode('UTF-8')), encoding='utf-8')
		# decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)).decode())


		if decrypted['watermark']['appid'] != self.appId:
			raise Exception('Invalid Buffer')

		return decrypted

	def _unpad(self, s):
		return s[:-ord(s[len(s)-1:])]



# https://www.cnblogs.com/Xingtxx/p/10937043.html

# decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))
# self._unpad(cipher.decrypt(encrypted_data)) 这个方法是得到一个 bytes 类型数据所以需要解码
# json.loads()　　这个方法需要str 是不会 bytes 否则报错
# json.loads()　　是json格式处理函数（可以这么理解，json是字符串）
# json.loads()   用于解码 JSON 数据。该函数返回 Python 字段的数据类型。
# json.loads() 　如果字符串不是字典格式的字符串的时候，执行json.loads会报错! 