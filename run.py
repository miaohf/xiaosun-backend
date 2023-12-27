from app import create_app, db
# from app.models import User

app = create_app()


# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User}


app.config['FLASKY_DB_QUERY_TIMEOUT'] = 5.0  # 设置sql执行超时时间，#记录执行时间超过 0.0001秒的
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 断开设置
app.config['SQLALCHEMY_RECORD_QUERIES'] = True  # 启用慢查询记录功能
 
 
# from flask_sqlalchemy import get_debug_queries
 
 
# @app.after_request
# def after_request(response):
#     for query in get_debug_queries():
#         if query.duration >= app.config['FLASKY_DB_QUERY_TIMEOUT']:
#             print('#####Slow query:%s \nParameters:%s \nDuration:%fs\nContext:%s\n #####' %
#                   (query.statement, query.parameters, query.duration,query.context))  # 打印超时sql执行信息
#     return response
 
 
@app.teardown_request
def handle_teardown_request(ex):
    db.session.remove()



if __name__ == '__main__':
    app.run(debug=True)