/*
Navicat MySQL Data Transfer

Source Server         : MySql
Source Server Version : 80013
Source Host           : localhost:3306
Source Database       : t

Target Server Type    : MYSQL
Target Server Version : 80013
File Encoding         : 65001

Date: 2022-03-21 10:56:20
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for spider_gongzhonghao_result
-- ----------------------------
DROP TABLE IF EXISTS `spider_gongzhonghao_result`;
CREATE TABLE `spider_gongzhonghao_result` (
  `un_id` int(11) NOT NULL COMMENT '对应学校主键',
  `url` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '请求的URL',
  `title` varchar(255) DEFAULT NULL COMMENT '标题',
  `content` text CHARACTER SET utf8 COLLATE utf8_general_ci COMMENT '当前页面下所有的可见文字',
  `chrono` int(11) DEFAULT NULL COMMENT '信息发布日期',
  `type` int(11) NOT NULL DEFAULT '0' COMMENT '类型',
  `count` int(11) DEFAULT '0' COMMENT '点击次数',
  `last_scan_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新扫描时间',
  `last_update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='公众号爬虫';
