# Spider_GongZhongHao
微信公众号爬虫，根据指定公众号名称，爬取该公众号所有文章。

需要自己注册微信公众号，登陆以后在网页中获取Cookie值。

一个cookie一天大约可以爬取800篇文章，超出后大概率会被封几个小时。

如果需要快速大量爬取多个公众号文章，可以尝试注册一个订阅号，同时配置多个运营人员（5个长期、20个短期），这样就可以同时拥有多个cookie来爬取。



使用说明：

- config字段配置：

  ```json
  {
    "official_accounts_name": [],  公众号名称，爬虫会根据公众号名称搜索，请保证精确，支持
    "un_id": {},                   保存到数据库的ID
    "cur_serial_number": {},       当前爬取的条数，爬虫会根据此数据开始进行爬取，中途会持续更新该字段
    "cookies": [],                 需要注册订阅号，登录后拿到该cookie值，建议存储多个
    "mysql_connect": {             如果需要保存数据到数据库，需要填写此处配置
      "ip_address": "",
      "port_number": 3340,
      "username": "",
      "password": "",
      "db_name": ""
    }
  }
  ```

- 启动

  ```python
  下载相关的依赖
  python spider.py
  ```

  

