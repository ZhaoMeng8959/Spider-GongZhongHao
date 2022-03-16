SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `spider_gongzhonghao_result`;
CREATE TABLE `spider_gongzhonghao_result` (
  `un_id` int(11) NOT NULL COMMENT '对应学校主键',
  `url` varchar(255) NOT NULL COMMENT '请求的URL',
  `title` varchar(255) DEFAULT NULL COMMENT '标题',
  `content` varchar(2550) DEFAULT NULL COMMENT '当前页面下所有的可见文字',
  `chrono` int(11) DEFAULT NULL COMMENT '信息发布日期',
  `type` int(11) NOT NULL DEFAULT '0' COMMENT '类型',
  `count` int(11) DEFAULT '0' COMMENT '点击次数',
  `last_scan_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新扫描时间',
  `last_update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='电子科技大学';
