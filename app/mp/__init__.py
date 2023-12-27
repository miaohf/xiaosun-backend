from flask import Blueprint

bp = Blueprint('mp', __name__)

# 写在最后是为了防止循环导入，ping.py文件也会导入 bp
from app.mp import main, menu, click
