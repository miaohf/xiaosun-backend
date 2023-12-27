
from wechatpy import WeChatClient
from wechatpy.replies import TextReply, ArticlesReply
from wechatpy.utils import ObjectDict

from flask import jsonify

from sqlalchemy import func

from app import create_app, db

import json

app=create_app()
app.app_context().push()
from app.models import Houses, Gardens


client = WeChatClient('wx5233798c91b12aa8', '3888aa02c423a8a11e5c41a469eb3ce8')


def serialize(self):
    return {c: getattr(self, c) for c in inspect(self).attrs.keys()}


class MenuClick(object):
    def __init__(self, msg, ):
        self.msg = msg
        # self.path = current_app.config['CODE_PATH'],
        # redis_client = Redis.from_url(current_app.config['REDIS_STORAGE'])
        # session_interface = RedisStorage(
        #     redis_client,
        #     prefix="ACCESS_TOKEN"
        # )
        self.client = WeChatClient(
            'wx5233798c91b12aa8', 
            '3888aa02c423a8a11e5c41a469eb3ce8',
            # session=session_interface
        )
        print('MenuClick')

    # 根据点击的按钮实际完成相应的操作
    def menu_click(self):
        try:
            return getattr(self, self.msg.key)()
        except Exception as e:
            print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
            print('错误所在的行号：', e.__traceback__.tb_lineno)
            print(e)
            return self.return_text("未知操作")

    # 处理换号提醒
    # def change_number(self):
    #         wx_message = "您好，请输入您当前使用的号码，我们帮你换新号。"
    #         return self.return_text(wx_message)
    # 
    def houseQuery_01(self):
        houses_details = Houses.query\
            .join(Gardens, Houses.garden_id == Gardens.id)\
            .filter(Gardens.id == 1)\
            .with_entities(func.count(Houses.id), Gardens.name, Houses.status)\
            .group_by(Gardens.name, Houses.status).all()


        print(houses_details)

        description = {
            '未选': 0,
            '已选': 0,
        }

        temp_dict = {}
        for d in houses_details:
        
            if d[2] == 1:
                temp_dict['未选'] = d[0]
            else:
                temp_dict['已选'] = d[0]
        
        description.update(temp_dict)

        articles = [{
            'title': '01.大西门3#地块',
            'description': str(description) + '【点击清单(请横屏查看)，仅供参考】',
            'url': 'http://xuanfang.tuozhanad.com/#/mp/mp/1',
            'image': 'http://xuanfang.tuozhanad.com/img/magic_deer2.jpg'
            }
        ]

        print('articles:', type(articles))

        self.client.message.send_articles(self.msg.source, articles)
        return 'ok'

    def houseQuery_02(self):
        houses_details = Houses.query\
            .join(Gardens, Houses.garden_id == Gardens.id)\
            .filter(Gardens.id == 2)\
            .with_entities(func.count(Houses.id), Gardens.name, Houses.status)\
            .group_by(Gardens.name, Houses.status).all()
        
        description = {
            '未选': 0,
            '已选': 0,
        }

        temp_dict = {}
        for d in houses_details:
        
            if d[2] == 1:
                temp_dict['未选'] = d[0]
            else:
                temp_dict['已选'] = d[0]
        
        description.update(temp_dict)


        articles = [{
            'title': '02.大西门2#地块',
            'description': str(description) + '【点击清单(请横屏查看)，仅供参考】',
            'url': 'http://xuanfang.tuozhanad.com/#/mp/mp/2',
            'image': 'http://xuanfang.tuozhanad.com/img/magic_deer2.jpg'
            }
        ]

        print('articles:', type(articles))

        self.client.message.send_articles(self.msg.source, articles)
        return 'ok'

    def houseQuery_03(self):
        houses_details = Houses.query\
            .join(Gardens, Houses.garden_id == Gardens.id)\
            .filter(Gardens.id == 3)\
            .with_entities(func.count(Houses.id), Gardens.name, Houses.status)\
            .group_by(Gardens.name, Houses.status).all()

        description = {
            '未选': 0,
            '已选': 0,
        }

        temp_dict = {}
        for d in houses_details:
        
            if d[2] == 1:
                temp_dict['未选'] = d[0]
            else:
                temp_dict['已选'] = d[0]
        
        description.update(temp_dict)


        articles = [{
            'title': '03.大西门1#地块',
            'description': str(description) + '【点击清单(请横屏查看)，仅供参考】',
            'url': 'http://xuanfang.tuozhanad.com/#/mp/mp/3',
            'image': 'http://xuanfang.tuozhanad.com/img/magic_deer2.jpg'
            }
        ]

        print('articles:', type(articles))

        self.client.message.send_articles(self.msg.source, articles)
        return 'ok'


    def houseQuery_04(self):
        houses_details = Houses.query\
            .join(Gardens, Houses.garden_id == Gardens.id)\
            .filter(Gardens.id == 4)\
            .with_entities(func.count(Houses.id), Gardens.name, Houses.status)\
            .group_by(Gardens.name, Houses.status).all()

        description = {
            '未选': 0,
            '已选': 0,
        }

        temp_dict = {}
        for d in houses_details:
        
            if d[2] == 1:
                temp_dict['未选'] = d[0]
            else:
                temp_dict['已选'] = d[0]
        
        description.update(temp_dict)


        articles = [{
            'title': '04.直属库地块',
            'description': str(description) + '【点击清单(请横屏查看)，仅供参考】',
            'url': 'http://xuanfang.tuozhanad.com/#/mp/mp/4',
            'image': 'http://xuanfang.tuozhanad.com/img/magic_deer2.jpg'
            }
        ]

        print('articles:', type(articles))

        self.client.message.send_articles(self.msg.source, articles)
        return 'ok'


    def houseQuery_05(self):
        houses_details = Houses.query\
            .join(Gardens, Houses.garden_id == Gardens.id)\
            .filter(Gardens.id == 5)\
            .with_entities(func.count(Houses.id), Gardens.name, Houses.status)\
            .group_by(Gardens.name, Houses.status).all()

        description = {
            '未选': 0,
            '已选': 0,
        }

        temp_dict = {}
        for d in houses_details:
        
            if d[2] == 1:
                temp_dict['未选'] = d[0]
            else:
                temp_dict['已选'] = d[0]
        
        description.update(temp_dict)


        articles = [{
            'title': '05.家英小区南侧地块',
            'description': str(description) + '【点击清单(请横屏查看)，仅供参考】',
            'url': 'http://xuanfang.tuozhanad.com/#/mp/mp/5',
            'image': 'http://xuanfang.tuozhanad.com/img/magic_deer2.jpg'
            }
        ]

        print('articles:', type(articles))

        self.client.message.send_articles(self.msg.source, articles)
        return 'ok'

        
    # 描述性文字
    def return_text(self, text):
        reply = TextReply(message=self.msg)
        reply.content = text
        # 转换成 XML
        xml = reply.render()
        return xml

    # 发送照片
    def send_img(self):
        # 调用系统函数
        # 拍照截图 图片为类型+时间戳.jpg
        # img_file = "类型+时间戳.jpg"
        img_file = PiSysCall(self.path[0]).monitor()
        img = open(img_file, 'rb')
        img_upload = self.client.media.upload('image', img)
        self.client.message.send_image(self.msg.source, img_upload['media_id'])
