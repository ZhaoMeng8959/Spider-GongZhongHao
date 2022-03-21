# Spider_GongZhongHao
微信公众号爬虫，根据指定公众号名称，爬取该公众号所有文章。

需要自己注册微信公众号，登陆以后在网页中获取Cookie值。



使用说明：

- config字段配置：

  ```json
  {
    "official_accounts_name": [],  【必填】公众号名称，爬虫会根据公众号名称搜索，请保证精确，支持
    "un_id": {},                   【必填】保存到数据库的ID
    "cur_serial_number": {},       【必填】当前爬取的条数，爬虫会根据此数据开始进行爬取，中途会持续更新该字段，默认从0开始
    "cookies": [],                 【必填】需要注册订阅号，登录后拿到该cookie值，建议存储多个
    "spider_pattern": 0,           【必填】抓取模式: 0：全部抓取，抓取过的文章也抓取，这里会判断更新时间，更新过的数据才会保存；1：仅抓取未抓取的文章；目前仅针对数据库使用
    "save_to_file": false,         【必填】是否保存到文件中
    "save_to_mysql": true,         【必填】是否保存到数据库，若需要，需要填写数据库连接信息
    "mysql_connect": {             【必填】如果需要保存数据到数据库，需要填写此处配置
      "ip_address": "",
      "port_number": 3306,
      "username": "",
      "password": "",
      "db_name": ""
    }
  }
  ```

- 启动

  ```python
  1. 下载相关的依赖
  2. 执行: python spider.py
  ```

  

