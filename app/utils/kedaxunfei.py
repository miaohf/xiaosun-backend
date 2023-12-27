# -*- coding:utf-8 -*-

import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os


STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

# 讯飞小燕    普通话 xiaoyan   已开通
# 讯飞许久    普通话 aisjiuxu    已开通
# 讯飞小萍    普通话 aisxping    已开通
# 讯飞小婧    普通话 aisjinger   已开通
# 讯飞许小宝   普通话 aisbabyxu   已开通


class generate_audio:
    
    # def __init__(self, APPID, APIKey, APISecret, Text):
    def __init__(self, pcm_sequence, text, output_file, voice_name):
        # print(text, output_file)

        self.APPID = 'fc655f56'
        self.APIKey='ec4bfd6e0394962b97b0bae83a28a4a4'
        self.APISecret='ZGU1NWJlMDUwMDc4OTQ3ZWFiNzI4NDU2'

        # self.APPID = 'fdf1f9a4'
        # self.APIKey='MTJlNGE3ZmI2NmRlYTRlMGNjMmNjNDZm'
        # self.APISecret='0d1074eea505452629a08e536959b898'
        self.Text=text
        self.CommonArgs = {"app_id": self.APPID}
        self.pcm_file = '/tmp/' + pcm_sequence + '.pcm'
        # 业务参数(business)，更多个性化参数可在官网查看
        # self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "x2_qianqian", "tte": "utf8"}
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": voice_name, "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}

        websocket.enableTrace(False)
        # websocket.enableTrace(True)

        print('self.BusinessArgs: ', self.BusinessArgs)
        wsUrl = self.create_url()

        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)

        self.ws = ws
        self.ws.on_open = self.on_open
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.convert_to_mp3(output_file)
        

    def convert_to_mp3(self, output_file):
        command = 'ffmpeg ' + '-y -f s16le -ar 16000 -i ' + self.pcm_file + ' ' + output_file
        os.system(command)


    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        return url

    def on_message(self, ws, message):
        try:
            message =json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            # print(message)
            if status == 2:
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:

                with open(self.pcm_file, 'ab') as f:
                    f.write(audio)

        except Exception as e:
            print("receive msg,but parse exception:", e)


    def on_error(self, ws, error):
        return error

    def on_close(self, ws, *args):
        print("### closed ###")

    def on_open(self, ws):
        thread.start_new_thread(self.run, ())

    def run(self, *args):
        d = {"common": self.CommonArgs,
             "business": self.BusinessArgs,
             "data": self.Data,
             }
        d = json.dumps(d)
        print("------>开始发送文本数据")
        self.ws.send(d)

        print("------>文本发送完成")

        if os.path.exists('/tmp/xuanfang.pcm'):
            os.remove('/tmp/xuanfang.pcm')






# 成年女声：
# 1, 阅读场景 百合仙子
# 2，广告场景 小南

# 第1号，户主姓名周弟弟，本轮共抽取4套。第1套: 善智苑二期 1幢1单元301室，面积108.0平米。 第2套: 善智苑二期 1幢1单元301室，面积108.0平米。 第3套: 善智苑二期 1幢1单元301室，面积108.0平米。第4套: 善智苑二期 1幢1单元301室，面积108.0平米。

# 成年男声：
# 1，阅读场景 超哥
# 2，阅读场景 刚哥
# 3，阅读场景 七哥


# 请，第”003“号，张利丰准备。



# 1,讯飞小露 x2_yezi
# 2,讯飞倩倩 x2_qianqian
# 2,讯飞小莫 x2_xiaomo
# 3,讯飞一菲 x2_yifei
# 4.讯飞小婉 x2_xiaowan #情感热线

# 1,讯飞超哥 x2_chaoge
# 2,讯飞楠楠 x2_nannan
# 3,讯飞小雅 x2_xiaoya
# 4,讯飞一峰 x2_yifeng
# 5,讯飞水哥 x2_xiaoxi
# 6,讯飞小魏 x_xiaowei  #太慢