/*
 Navicat Premium Dump SQL

 Source Server Type    : MySQL
 Source Schema         : ls_taxi

 Target Server Type    : MySQL
 Target Server Version : 50744 (5.7.44-log)
 File Encoding         : 65001

 Date: 15/01/2025 12:18:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for intercity_route
-- ----------------------------
DROP TABLE IF EXISTS `intercity_route`;
CREATE TABLE `intercity_route`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '路线ID',
  `start_city` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '出发城市',
  `end_city` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '到达城市',
  `start_station` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '出发站点',
  `end_station` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '到达站点',
  `car_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '车型（舒适型、商务型、豪华型、七座商务）',
  `price` decimal(10, 2) NOT NULL COMMENT '价格（元）',
  `estimated_time` int(11) NOT NULL COMMENT '预计时间（分钟）',
  `status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '状态（0：正常，-1：禁用）',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_start_city`(`start_city`) USING BTREE,
  INDEX `idx_end_city`(`end_city`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '城际路线表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_company
-- ----------------------------
DROP TABLE IF EXISTS `ls_company`;
CREATE TABLE `ls_company`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '公司名称',
  `short_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '简称如：曹操出行',
  `contact` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '地址',
  `phone` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '联系电话',
  `service_phone` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '客服电话',
  `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `license_no` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `license_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `region_id` int(11) NULL DEFAULT NULL COMMENT '所在区域ID',
  `allow_region` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '所能接单区域id表',
  `region` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '所在地区',
  `type` smallint(6) NULL DEFAULT 0 COMMENT '0=总部公司,1=区域代理商',
  `status` smallint(6) NULL DEFAULT 0 COMMENT '0=正常,-1禁用',
  `bz` text CHARACTER SET utf8 COLLATE utf8_bin NULL,
  `created_at` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `uid` int(11) NULL DEFAULT NULL,
  `commission_rate` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '加盟商佣金比率',
  `driver_rate` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '司机佣金比率',
  `updated_at` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '运营公司表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_company_comission
-- ----------------------------
DROP TABLE IF EXISTS `ls_company_comission`;
CREATE TABLE `ls_company_comission`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) NULL DEFAULT NULL COMMENT '运营商ID',
  `total_fee` decimal(10, 2) NULL DEFAULT NULL COMMENT '总收入',
  `amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '佣金',
  `remark` text CHARACTER SET utf8 COLLATE utf8_bin NULL COMMENT '说明',
  `created_at` datetime NULL DEFAULT NULL COMMENT '结算时间',
  `uid` int(11) NULL DEFAULT NULL COMMENT '结算用户',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '运营公司佣金管理' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_company_map
-- ----------------------------
DROP TABLE IF EXISTS `ls_company_map`;
CREATE TABLE `ls_company_map`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) NOT NULL COMMENT '公司ID',
  `center_lng` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '圆心经度',
  `center_lat` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '圆心纬度',
  `radius` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '半径(米)',
  `path_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '圆形路径数据(JSON格式)',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `latlng` geometry NULL COMMENT '使用 GEOMETRY 类型存储多边形',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_coupon_cash
-- ----------------------------
DROP TABLE IF EXISTS `ls_coupon_cash`;
CREATE TABLE `ls_coupon_cash`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `coupon_id` bigint(20) NOT NULL COMMENT '优惠券ID',
  `amount` decimal(10, 2) NOT NULL COMMENT '代金券面额(元)',
  `condition_type` smallint(6) NOT NULL DEFAULT 0 COMMENT '使用条件类型(0:无门槛,1:满额使用)',
  `condition_amount` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '使用条件金额(condition_type=1时有效)',
  `created_at` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `updated_at` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_coupon_id`(`coupon_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '代金券特定信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_coupons
-- ----------------------------
DROP TABLE IF EXISTS `ls_coupons`;
CREATE TABLE `ls_coupons`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '优惠券ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '优惠券名称',
  `type` smallint(6) NULL DEFAULT NULL COMMENT '优惠券类型(0:代金券,1:满减2l:拉新)',
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '优惠券编码',
  `total_num` int(11) NULL DEFAULT NULL COMMENT '发放总量',
  `surplus` int(11) NULL DEFAULT NULL COMMENT '剩余数量',
  `limit_num` int(11) NULL DEFAULT 1 COMMENT '每人限领数量',
  `valid_type` smallint(6) NULL DEFAULT NULL COMMENT '有效期类型(0:固定日期,1:动态有效期)',
  `start_date` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '有效期开始时间(valid_type=0时有效)',
  `end_date` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '有效期结束时间(valid_type=0时有效)',
  `valid_days` int(11) NULL DEFAULT NULL COMMENT '有效天数(valid_type=1时有效)',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '优惠券说明',
  `status` smallint(6) NULL DEFAULT 0 COMMENT '状态0=可用状态,-1过期不可用',
  `uid` bigint(20) NULL DEFAULT NULL COMMENT '创建人ID',
  `amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '面额',
  `condition_amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '使用条件金额',
  `use_object` smallint(6) NULL DEFAULT NULL COMMENT '拉新券时有效(0邀请人,10被邀请人,11双方)',
  `use_city` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '适用城市',
  `use_range` smallint(6) NULL DEFAULT NULL COMMENT '0=快车，1=城际快车,拉新券时可用于所有',
  `created_at` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '创建时间',
  `updated_at` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_code`(`code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '优惠券基础信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_coupons_list
-- ----------------------------
DROP TABLE IF EXISTS `ls_coupons_list`;
CREATE TABLE `ls_coupons_list`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `utype` smallint(6) NULL DEFAULT 0 COMMENT '0=乘客,1=司机',
  `uid` int(11) NULL DEFAULT NULL COMMENT 'uid',
  `phone` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '领用人电话',
  `truename` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '领用人姓名',
  `take_code` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '领用编码',
  `coupon_id` int(11) NULL DEFAULT NULL,
  `status` smallint(6) NULL DEFAULT NULL COMMENT '0=未使用，1=已使用，-1=过期',
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '领取时间',
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '使用时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '优惠券领用表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_device_vehicle_license
-- ----------------------------
DROP TABLE IF EXISTS `ls_device_vehicle_license`;
CREATE TABLE `ls_device_vehicle_license`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `driver_id` bigint(20) NULL DEFAULT NULL COMMENT '关联用户ID',
  `car_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '车牌号码',
  `car_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '车辆类型',
  `owner` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所有人',
  `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '住址',
  `use_character` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '使用性质',
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '品牌型号',
  `vin` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '车辆识别代号',
  `engine_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发动机号码',
  `register_date` date NULL DEFAULT NULL COMMENT '注册日期',
  `issue_date` date NULL DEFAULT NULL COMMENT '发证日期',
  `file_front` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '行驶证正面照片URL',
  `file_back` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '行驶证背面照片URL',
  `status` tinyint(4) NULL DEFAULT 1 COMMENT '状态(0-无效 1-有效)',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_plate_number`(`car_no`) USING BTREE,
  INDEX `idx_device_id`(`driver_id`) USING BTREE,
  INDEX `idx_vin`(`vin`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '行驶证信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver`;
CREATE TABLE `ls_driver`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `region_id` int(11) NULL DEFAULT NULL COMMENT '所属于区域',
  `username` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `password` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `token` varchar(200) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `truename` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `phone` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `avatar` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '头像',
  `sex` smallint(6) NULL DEFAULT 0 COMMENT '0=男，1=女',
  `id_card` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '身份证',
  `id_card_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `id_card_img1` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `driving_age` int(11) NULL DEFAULT NULL COMMENT '驾龄',
  `face_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '司机正面照',
  `score` float NULL DEFAULT 0 COMMENT '综合评分',
  `insure_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '保单照片',
  `car_no` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车牌号',
  `car_age` int(11) NULL DEFAULT NULL COMMENT '车龄',
  `car_brand` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '品牌',
  `car_color` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车辆颜色',
  `car_type` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车辆类型,轿车,suv',
  `last_ip` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `last_time` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '最近登录时间',
  `company_id` int(11) NULL DEFAULT NULL COMMENT '司机所属运营公司',
  `company_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `commission_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT '司机佣金比率',
  `recommend_uid` int(11) NULL DEFAULT NULL COMMENT '推荐司机ID',
  `work_status` smallint(6) NULL DEFAULT 0 COMMENT '0=下班（不可接单）1=上班状态，2=休息状态(不可接单)，3=正在接送客户',
  `accept_order_model` smallint(6) NULL DEFAULT 0 COMMENT '0=系统单，1=抢单(自动)',
  `online_total_time` int(11) NULL DEFAULT NULL COMMENT 'APP总在线时长（秒）',
  `today_online_total_time` int(11) NULL DEFAULT 0 COMMENT '当天在线时长',
  `total_online_time` int(11) NULL DEFAULT 0 COMMENT '总在线时长',
  `status` smallint(6) NULL DEFAULT 0 COMMENT '0=正常，-1禁止，-9司机待审核',
  `level` smallint(6) NULL DEFAULT 1 COMMENT '1默认级别',
  `accept_order_status` smallint(6) NULL DEFAULT 0 COMMENT '0=未在接送状态，1=在服务乘客状态不可再接单',
  `bank_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `bank_card` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '卡号',
  `order_total` int(11) NULL DEFAULT 0 COMMENT '司机订单总数，为方便统计',
  `uid` int(11) NULL DEFAULT NULL,
  `birthday` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '注册日期',
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `no_air` smallint(6) NULL DEFAULT 0 COMMENT '不接机场',
  `no_train` smallint(6) NULL DEFAULT 0,
  `on_way_address` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT '顺路单：地址#lng,lat#0.6',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '司机表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_account
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_account`;
CREATE TABLE `ls_driver_account`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `driver_id` bigint(20) NULL DEFAULT NULL COMMENT '司机ID',
  `order_id` bigint(20) NULL DEFAULT NULL COMMENT '收入时的订单ID',
  `amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '金额+,-',
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '帐目说明',
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '入帐时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '司机帐目表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_license
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_license`;
CREATE TABLE `ls_driver_license`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `driver_id` bigint(20) NULL DEFAULT NULL COMMENT '关联用户ID',
  `no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '驾驶证号',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '姓名',
  `sex` tinyint(4) NULL DEFAULT 0 COMMENT '性别(0男 1-女)',
  `nationality` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '国籍',
  `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '住址',
  `birth_date` date NULL DEFAULT NULL COMMENT '出生日期',
  `issue_date` date NULL DEFAULT NULL COMMENT '初次领证日期',
  `license_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '准驾车型',
  `start_date` date NULL DEFAULT NULL COMMENT '有效期起始日',
  `end_date` date NULL DEFAULT NULL COMMENT '有效期截止日',
  `issuing_authority` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发证机关',
  `pic_front` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '驾驶证正面照片URL',
  `pic_back` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '驾驶证背面照片URL',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '状态',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_license_number`(`no`) USING BTREE,
  INDEX `idx_driver_id`(`driver_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '驾驶证信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_location
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_location`;
CREATE TABLE `ls_driver_location`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) NULL DEFAULT 0 COMMENT '所在公司id',
  `driver_id` int(11) NOT NULL,
  `location` point NOT NULL,
  `address` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `status` smallint(6) NULL DEFAULT 1,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `latlng` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '最后坐标位置',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_driver_id`(`driver_id`) USING BTREE,
  SPATIAL INDEX `idx_location`(`location`),
  INDEX `updated_at`(`updated_at`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 105 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '司机实时位置表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_online_time
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_online_time`;
CREATE TABLE `ls_driver_online_time`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `driver_id` int(11) NULL DEFAULT NULL,
  `online_total_time` int(11) NULL DEFAULT NULL COMMENT '在线时长秒',
  `created_at` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '日期',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci COMMENT = '司机每天在线时长' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_order_accept
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_order_accept`;
CREATE TABLE `ls_driver_order_accept`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NULL DEFAULT NULL COMMENT '订单ID',
  `driver_id` int(11) NULL DEFAULT NULL,
  `order_type_text` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文字说明订单类型',
  `send_time` datetime NULL DEFAULT NULL COMMENT '发布时间',
  `accept_time` datetime NULL DEFAULT NULL COMMENT '接单时间',
  `second` int(11) NULL DEFAULT NULL COMMENT '持续时长',
  `lat` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接单时位置坐标',
  `lng` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `distance` int(11) NULL DEFAULT NULL COMMENT '司机接单号离乘客距离',
  `status` smallint(6) NULL DEFAULT 0 COMMENT '0=未接单，1=已接单，-1=拒绝接单,-2=超时无人接单,-3=乘客主动取消',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `driver_index`(`driver_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 608 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '司机抢单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_register
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_register`;
CREATE TABLE `ls_driver_register`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `truename` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '真实姓名',
  `phone` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '电话',
  `id_card` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '身份证',
  `id_card_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '身份证',
  `id_card_img1` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '身份证反面',
  `driving_age` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '驾龄',
  `driving_licence` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '驾驶证照片',
  `driving_licence1` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '驾驶证照片反面',
  `car_licence` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '行驶证照片',
  `car_licence1` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '行驶证照片反面',
  `car_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车辆照片',
  `car_img1` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `insure_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '保险照片',
  `car_no` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车牌',
  `car_age` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车龄',
  `car_brand` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车辆品牌',
  `car_color` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车辆颜色',
  `car_type` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '车辆类型',
  `recommend_uid` int(11) NULL DEFAULT NULL COMMENT '推荐人',
  `recommend_phone` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `recommend_name` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `region_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '所在区域',
  `status` smallint(6) NULL DEFAULT 0 COMMENT '0=待审核，1=通过，-1=拒绝',
  `created_at` datetime NULL DEFAULT NULL COMMENT '注册时间',
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `birthday` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '司机注册表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_reject_log
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_reject_log`;
CREATE TABLE `ls_driver_reject_log`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NULL DEFAULT NULL,
  `driver_id` int(11) NULL DEFAULT NULL,
  `num` int(11) NULL DEFAULT 0 COMMENT '同订单已经拒绝了多少次',
  `created_at` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci COMMENT = '司机接单拒绝记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_score_log
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_score_log`;
CREATE TABLE `ls_driver_score_log`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `driver_id` int(11) NULL DEFAULT NULL,
  `score` float NULL DEFAULT NULL COMMENT '增加或减少的分值',
  `remark` varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci COMMENT = '司机分值记录' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_driver_take_cash
-- ----------------------------
DROP TABLE IF EXISTS `ls_driver_take_cash`;
CREATE TABLE `ls_driver_take_cash`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `driver_id` int(11) NULL DEFAULT NULL,
  `amount` decimal(10, 2) NULL DEFAULT NULL,
  `bank_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '银行名称',
  `bank_card` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '银行卡',
  `status` smallint(6) NULL DEFAULT NULL COMMENT '0待审核，1=审核中，2=已通过，3=已拒绝，4=已打款',
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '申请时间',
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '提现申请表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_invoice
-- ----------------------------
DROP TABLE IF EXISTS `ls_invoice`;
CREATE TABLE `ls_invoice`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键ID',
  `invoice_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '发票申请ID（业务ID）',
  `user_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
  `user_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名',
  `user_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户手机号',
  `invoice_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'personal' COMMENT '发票类型：personal-个人，company-企业',
  `invoice_title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发票抬头（企业发票必填）',
  `tax_number` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '纳税人识别号（企业发票必填）',
  `amount` decimal(12, 2) NULL DEFAULT NULL COMMENT '发票金额',
  `email` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收电子发票的邮箱',
  `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'pending' COMMENT '状态：pending-待处理，approved-已通过，rejected-已拒绝，issued-已开具',
  `apply_time` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '申请时间',
  `process_time` datetime NULL DEFAULT NULL COMMENT '处理时间',
  `processor` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '处理人',
  `reject_reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '拒绝原因',
  `invoice_file` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发票文件路径',
  `invoice_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发票代码',
  `invoice_number` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发票号码',
  `issue_time` datetime NULL DEFAULT NULL COMMENT '开具时间',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_invoice_id`(`invoice_id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE,
  INDEX `idx_apply_time`(`apply_time`) USING BTREE,
  INDEX `idx_process_time`(`process_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '发票申请表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_map_fence
-- ----------------------------
DROP TABLE IF EXISTS `ls_map_fence`;
CREATE TABLE `ls_map_fence`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `region_id` int(11) NULL DEFAULT NULL COMMENT '所属区域',
  `company_id` int(11) NULL DEFAULT NULL COMMENT '所属公司ID',
  `latlng` text CHARACTER SET utf8 COLLATE utf8_bin NULL COMMENT '可使用的电子围栏范围',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '地图围栏' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_navi
-- ----------------------------
DROP TABLE IF EXISTS `ls_navi`;
CREATE TABLE `ls_navi`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NULL DEFAULT NULL,
  `driver_id` int(11) NULL DEFAULT NULL,
  `latlng` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `speed` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `accuracy` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `put_time` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_order_id`(`order_id`) USING BTREE,
  INDEX `idx_driver_id`(`driver_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12246 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order
-- ----------------------------
DROP TABLE IF EXISTS `ls_order`;
CREATE TABLE `ls_order`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sn` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '订单编号',
  `region_id` int(11) NULL DEFAULT NULL COMMENT '订单所属于区域ID',
  `customer_id` int(11) NULL DEFAULT NULL COMMENT '乘客ID',
  `start_location` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '出发地',
  `start_latlng` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '上车地坐标',
  `end_location` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '目的地',
  `end_latlng` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '下车地坐标',
  `distance` int(11) NULL DEFAULT NULL COMMENT '订单路程(米)',
  `duration` int(11) NULL DEFAULT NULL COMMENT '预计用时(秒)',
  `cost` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '预估费用',
  `tolls` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '0' COMMENT '路段收费费用，元',
  `ev_price` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `order_time` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '下单时间',
  `up_time` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '上车时间',
  `down_time` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '下车时间',
  `driver_id` int(11) NULL DEFAULT 0 COMMENT '司机ID',
  `waiting_time` int(11) NULL DEFAULT 0 COMMENT '等待时长(秒）',
  `accept_time` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '接单时间',
  `trip_time` int(11) NULL DEFAULT NULL COMMENT '行程用时时长',
  `add_price` decimal(10, 2) NULL DEFAULT NULL COMMENT '是否有加价',
  `total_fee` decimal(10, 2) NULL DEFAULT NULL COMMENT '订单费用,未结算时显示预估价',
  `pay_amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '支付金额',
  `real_pay_amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '微信实际支付金额',
  `discount_amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '优惠券金额',
  `pay_type` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '支付方式',
  `invoice` smallint(6) NULL DEFAULT 0 COMMENT '是否已开票',
  `status` smallint(6) NULL DEFAULT 0 COMMENT '0=待接单,1=已接单,2=乘客已上车,3=进行中,4=到达目的地(未支付)，5=已完成（支付),-1=用户取消，-2=无司机接单,6=正在接乘客途中',
  `order_type` smallint(6) NULL DEFAULT 0 COMMENT '0=普通订单(先用后付),1=先付后用订单',
  `is_dispatch` smallint(6) NULL DEFAULT 0 COMMENT '0=正常接单，1=调度派遣订单(系统派单)',
  `driver_commission` decimal(10, 2) NULL DEFAULT NULL COMMENT '司机佣金',
  `commission_settle` smallint(6) NULL DEFAULT 0 COMMENT '0=佣金未结算，1=已结算',
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `updated_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `find_num` int(11) NULL DEFAULT 0 COMMENT '此订单是第几次叫车',
  `customer_phone` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '乘客电话',
  `customer_token` varchar(200) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '乘客token用于通讯',
  `openid` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '乘客openid',
  `driver_name` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '司机姓名',
  `driver_phone` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '司机电话',
  `car_no` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `driver_lat` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `driver_lng` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '司机接单时坐标',
  `company_id` int(11) NULL DEFAULT 0 COMMENT '所属公司id',
  `company_ids` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT '打车时所选的车辆所属于公司列表 1,2,3形式',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `status_index`(`status`) USING BTREE,
  INDEX `updated_at_index`(`updated_at`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 406 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '订单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order_complaint
-- ----------------------------
DROP TABLE IF EXISTS `ls_order_complaint`;
CREATE TABLE `ls_order_complaint`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NULL DEFAULT NULL COMMENT '订单ID',
  `driver_id` int(11) NULL DEFAULT NULL,
  `content` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '投诉内容',
  `user_id` int(11) NULL DEFAULT NULL COMMENT '乘客ID',
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '处理结果',
  `created_at` datetime NULL DEFAULT NULL COMMENT '投诉时间',
  `updated_at` datetime NULL DEFAULT NULL COMMENT '处理时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '订单投诉表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order_fee_details
-- ----------------------------
DROP TABLE IF EXISTS `ls_order_fee_details`;
CREATE TABLE `ls_order_fee_details`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` bigint(20) NOT NULL,
  `start_fee` decimal(10, 2) NOT NULL COMMENT '分段起步费',
  `start_mileage` decimal(10, 2) NOT NULL COMMENT '分段起步里程，用于明确起步费对应的里程范围',
  `mileage_fee_per_km` decimal(10, 2) NOT NULL COMMENT '分段里程费单价',
  `extra_mileage` decimal(10, 2) NOT NULL COMMENT '超出起步里程的里程数',
  `duration_fee_per_minute` decimal(10, 2) NOT NULL COMMENT '分段时长费单价',
  `extra_duration_minutes` int(11) NOT NULL COMMENT '超出特定时长的时长数',
  `long_distance_fee` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '远途费',
  `long_distance_trigger_mileage` decimal(10, 2) NOT NULL COMMENT '触发远途费的里程数',
  `temporary_surcharge` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '临时加价费',
  `temporary_coefficent` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '临时加价系数1-100',
  `tolls` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '过路费',
  `insurance_id` int(11) NULL DEFAULT NULL COMMENT '保单ID',
  `insurance_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '保单费用',
  `coupon_id` int(11) NULL DEFAULT 0 COMMENT '优惠券ID',
  `coupon_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '优惠券名称',
  `discount` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '优惠券折扣',
  `user_add_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '用户加价叫车金额',
  `total_fee` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '总费用',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_order_id`(`order_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 242 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '订单费率明细表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order_heatmap
-- ----------------------------
DROP TABLE IF EXISTS `ls_order_heatmap`;
CREATE TABLE `ls_order_heatmap`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `location_type` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'start开始点，end终点',
  `latlng` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `order_count` int(11) NULL DEFAULT NULL,
  `total_fee` decimal(10, 2) NULL DEFAULT NULL,
  `created_at` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `address` text CHARACTER SET utf8 COLLATE utf8_bin NULL,
  `province` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `city` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `district` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `township` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 834 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci COMMENT = '当天订单热力图坐标数据' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order_hours_total
-- ----------------------------
DROP TABLE IF EXISTS `ls_order_hours_total`;
CREATE TABLE `ls_order_hours_total`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_num` int(11) NULL DEFAULT NULL COMMENT '订单数量',
  `order_fee` decimal(10, 2) NULL DEFAULT NULL COMMENT '订单金额',
  `hour` int(10) NULL DEFAULT NULL COMMENT '当前小时',
  `completed_num` int(11) NULL DEFAULT NULL COMMENT '完成订单数',
  `completed_fee` decimal(10, 2) NULL DEFAULT NULL COMMENT '完成订单金额',
  `cancel_num` int(11) NULL DEFAULT NULL COMMENT '取消数',
  `cancel_fee` decimal(10, 2) NULL DEFAULT NULL COMMENT '取消金额',
  `no_driver_num` int(11) NULL DEFAULT NULL COMMENT '无司机接单数',
  `no_driver_fee` decimal(10, 2) NULL DEFAULT NULL COMMENT '无司机接单订单金额',
  `created_at` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT '当前时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1705 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci COMMENT = '每小时订单统计' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order_payresult
-- ----------------------------
DROP TABLE IF EXISTS `ls_order_payresult`;
CREATE TABLE `ls_order_payresult`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `order_id` bigint(20) NULL DEFAULT NULL COMMENT '订单ID',
  `pay_body` text CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL COMMENT '支付json存储',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order_rating
-- ----------------------------
DROP TABLE IF EXISTS `ls_order_rating`;
CREATE TABLE `ls_order_rating`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `order_id` bigint(20) NULL DEFAULT NULL COMMENT '订单ID',
  `driver_id` int(11) NULL DEFAULT NULL COMMENT '司机ID',
  `score` float(5, 2) NULL DEFAULT NULL COMMENT '评分',
  `score_item` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '评分项',
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '用户评语',
  `user_id` int(11) NULL DEFAULT NULL COMMENT '乘客ID',
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '订单评价' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order_sequence
-- ----------------------------
DROP TABLE IF EXISTS `ls_order_sequence`;
CREATE TABLE `ls_order_sequence`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 194 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_order_transfer
-- ----------------------------
DROP TABLE IF EXISTS `ls_order_transfer`;
CREATE TABLE `ls_order_transfer`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` bigint(20) NULL DEFAULT NULL,
  `source_driver_id` int(11) NULL DEFAULT NULL,
  `target_driver_id` int(11) NULL DEFAULT NULL,
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `dispatch_id` int(11) NULL DEFAULT 0 COMMENT '调度员ID，0=表示司机转单',
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '订单转派表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_region
-- ----------------------------
DROP TABLE IF EXISTS `ls_region`;
CREATE TABLE `ls_region`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `parent_id` int(11) NULL DEFAULT NULL COMMENT '上级区域名称',
  `name` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '区域名称',
  `py` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `letter` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 483 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '运营区域表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_sms_code
-- ----------------------------
DROP TABLE IF EXISTS `ls_sms_code`;
CREATE TABLE `ls_sms_code`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `is_user` smallint(6) NULL DEFAULT 0 COMMENT '0=正常,-2=过期',
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 17 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_suggest
-- ----------------------------
DROP TABLE IF EXISTS `ls_suggest`;
CREATE TABLE `ls_suggest`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `content` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `contact` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `recontent` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT '' COMMENT '空时处理中',
  `uid` int(11) NULL DEFAULT NULL,
  `utype` smallint(6) NULL DEFAULT 0 COMMENT '0=司机，1=乘客',
  `created_at` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_sys_config
-- ----------------------------
DROP TABLE IF EXISTS `ls_sys_config`;
CREATE TABLE `ls_sys_config`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site_config` text CHARACTER SET utf8 COLLATE utf8_bin NULL COMMENT '存放系统配置',
  `customer_config` text CHARACTER SET utf8 COLLATE utf8_bin NULL COMMENT '乘客相关配置',
  `driver_config` text CHARACTER SET utf8 COLLATE utf8_bin NULL COMMENT '司机相关配置json',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_taxi_fee_settings
-- ----------------------------
DROP TABLE IF EXISTS `ls_taxi_fee_settings`;
CREATE TABLE `ls_taxi_fee_settings`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) NULL DEFAULT 0 COMMENT '所属加盟公司',
  `title` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT '时段描述',
  `start_time` time NULL DEFAULT NULL COMMENT '开始时间',
  `end_time` time NULL DEFAULT NULL,
  `start_fee` decimal(10, 2) NOT NULL COMMENT '分段起步费',
  `start_mileage` float NOT NULL COMMENT '分段起步里程',
  `mileage_fee_per_km` decimal(10, 2) NOT NULL COMMENT '分段里程费单价',
  `long_distance_trigger_mileage` float NOT NULL COMMENT '触发远途费的里程数',
  `long_distance_fee_per_km` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '远途费单价',
  `duration_fee_per_minute` decimal(10, 2) NOT NULL COMMENT '分段时长费单价',
  `is_default` smallint(6) NULL DEFAULT 0 COMMENT '1=默认时段，即不在所在时间段内',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_title`(`title`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '山租车费率表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_travel_price
-- ----------------------------
DROP TABLE IF EXISTS `ls_travel_price`;
CREATE TABLE `ls_travel_price`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `region_id` int(11) NOT NULL COMMENT '区域ID',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime NOT NULL COMMENT '结束时间',
  `price_per_km` decimal(5, 2) NOT NULL COMMENT '每公里价格',
  `bz` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注',
  `surcharge` decimal(5, 2) NULL DEFAULT NULL COMMENT '附加费用',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '各时段计费规则' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_user
-- ----------------------------
DROP TABLE IF EXISTS `ls_user`;
CREATE TABLE `ls_user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `password` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `truename` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `phone` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `is_admin` smallint(6) NULL DEFAULT 0 COMMENT '111=管理员,999=超级管理员',
  `utype` smallint(6) NULL DEFAULT 0 COMMENT '0=默认运营商用户,1=代理商,2=调度员',
  `parent_id` int(11) NULL DEFAULT NULL COMMENT '上级用户id',
  `company_id` int(11) NULL DEFAULT NULL COMMENT '所属公司',
  `status` smallint(6) NULL DEFAULT 0 COMMENT '0=正常，-1=禁用',
  `last_ip` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '最后登录ip',
  `last_time` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '最后登录时间',
  `created_at` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '后台用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_user_coupons
-- ----------------------------
DROP TABLE IF EXISTS `ls_user_coupons`;
CREATE TABLE `ls_user_coupons`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT '领取优惠券的用户 ID',
  `user_type` tinyint(1) NULL DEFAULT 0 COMMENT '0=乘客,1=司机',
  `coupon_id` int(11) NOT NULL COMMENT '领取的优惠券 ID',
  `receive_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '领取时间',
  `is_used` tinyint(1) NULL DEFAULT 0 COMMENT '是否已使用，0 表示未使用，1 表示已使用',
  `use_time` datetime NULL DEFAULT NULL COMMENT '使用时间，未使用时为 NULL',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '用户领取优惠券记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_user_log
-- ----------------------------
DROP TABLE IF EXISTS `ls_user_log`;
CREATE TABLE `ls_user_log`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NULL DEFAULT NULL,
  `utype` smallint(6) NULL DEFAULT 0,
  `content` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `ip` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 327 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '用户日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ls_wechat_user
-- ----------------------------
DROP TABLE IF EXISTS `ls_wechat_user`;
CREATE TABLE `ls_wechat_user`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `openid` varchar(80) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `token` varchar(200) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `phone` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '电话号码',
  `truename` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '真实姓名，如有',
  `nickname` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '昵称',
  `status` smallint(6) NULL DEFAULT 0 COMMENT '0=正常，1=禁用',
  `avatar` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '头像',
  `level` smallint(6) NULL DEFAULT 0 COMMENT '会员等级',
  `last_time` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '最近使用时间',
  `last_ip` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT 'ip',
  `recommend_uid` int(11) NULL DEFAULT 0 COMMENT '推荐的司机ID，0=无推荐',
  `utype` smallint(6) NULL DEFAULT 0 COMMENT '0=乘客,1=定义为调度员',
  `tpls` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '用户订阅的模板ID，以,号分隔，注意模板时间会过期',
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  FULLTEXT INDEX `phone`(`phone`)
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8 COLLATE = utf8_bin COMMENT = '乘客表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for v_accept_order
-- ----------------------------
DROP VIEW IF EXISTS `v_accept_order`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_accept_order` AS select `a`.`id` AS `accept_id`,`b`.`sn` AS `sn`,`b`.`region_id` AS `region_id`,`b`.`customer_id` AS `customer_id`,`b`.`start_location` AS `start_location`,`b`.`start_latlng` AS `start_latlng`,`b`.`end_location` AS `end_location`,`b`.`end_latlng` AS `end_latlng`,`b`.`distance` AS `distance`,`b`.`duration` AS `duration`,`b`.`cost` AS `cost`,`b`.`tolls` AS `tolls`,`b`.`order_time` AS `order_time`,`b`.`status` AS `status`,`b`.`order_type` AS `order_type`,`b`.`find_num` AS `find_num`,`b`.`customer_phone` AS `customer_phone`,`a`.`driver_id` AS `driver_id`,`a`.`order_id` AS `order_id`,`b`.`total_fee` AS `total_fee`,`b`.`customer_token` AS `customer_token`,`b`.`add_price` AS `add_price`,`b`.`created_at` AS `created_at`,`b`.`company_id` AS `company_id`,`b`.`pay_amount` AS `pay_amount`,`b`.`real_pay_amount` AS `real_pay_amount`,`b`.`discount_amount` AS `discount_amount`,`a`.`status` AS `accept_status`,`ls_order_fee_details`.`start_fee` AS `start_fee`,`ls_order_fee_details`.`start_mileage` AS `start_mileage`,`ls_order_fee_details`.`mileage_fee_per_km` AS `mileage_fee_per_km`,`ls_order_fee_details`.`extra_mileage` AS `extra_mileage`,`ls_order_fee_details`.`duration_fee_per_minute` AS `duration_fee_per_minute`,`ls_order_fee_details`.`extra_duration_minutes` AS `extra_duration_minutes`,`ls_order_fee_details`.`long_distance_fee` AS `long_distance_fee`,`ls_order_fee_details`.`long_distance_trigger_mileage` AS `long_distance_trigger_mileage`,`ls_order_fee_details`.`temporary_surcharge` AS `temporary_surcharge`,`ls_order_fee_details`.`temporary_coefficent` AS `temporary_coefficent`,`b`.`openid` AS `openid` from ((`ls_driver_order_accept` `a` join `ls_order` `b` on((`a`.`order_id` = `b`.`id`))) left join `ls_order_fee_details` on((`b`.`id` = `ls_order_fee_details`.`order_id`)));

-- ----------------------------
-- View structure for v_coupons_take_list
-- ----------------------------
DROP VIEW IF EXISTS `v_coupons_take_list`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_coupons_take_list` AS select `ls_coupons_list`.`utype` AS `utype`,`ls_coupons_list`.`uid` AS `uid`,`ls_coupons_list`.`status` AS `status`,`ls_coupons_list`.`created_at` AS `created_at`,`ls_coupons_list`.`updated_at` AS `updated_at`,`ls_coupons`.`id` AS `id`,`ls_coupons`.`name` AS `name`,`ls_coupons`.`type` AS `type`,`ls_coupons`.`code` AS `code`,`ls_coupons`.`total_num` AS `total_num`,`ls_coupons`.`surplus` AS `surplus`,`ls_coupons`.`limit_num` AS `limit_num`,`ls_coupons`.`valid_type` AS `valid_type`,`ls_coupons`.`start_date` AS `start_date`,`ls_coupons`.`end_date` AS `end_date`,`ls_coupons`.`valid_days` AS `valid_days`,`ls_coupons`.`description` AS `description`,`ls_coupons`.`status` AS `coupon_status`,`ls_coupons`.`amount` AS `amount`,`ls_coupons`.`condition_amount` AS `condition_amount`,`ls_coupons`.`use_object` AS `use_object`,`ls_coupons`.`use_city` AS `use_city`,`ls_coupons`.`use_range` AS `use_range`,`ls_coupons_list`.`phone` AS `phone`,`ls_coupons_list`.`truename` AS `truename`,`ls_coupons_list`.`take_code` AS `take_code`,`ls_coupons_list`.`id` AS `take_id` from (`ls_coupons` join `ls_coupons_list`) where (`ls_coupons`.`id` = `ls_coupons_list`.`coupon_id`) order by `ls_coupons_list`.`created_at` desc;

-- ----------------------------
-- View structure for v_driver_account
-- ----------------------------
DROP VIEW IF EXISTS `v_driver_account`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_driver_account` AS select `ls_driver_account`.`id` AS `id`,`ls_driver_account`.`driver_id` AS `driver_id`,`ls_driver_account`.`order_id` AS `order_id`,`ls_driver_account`.`remark` AS `remark`,`ls_driver_account`.`created_at` AS `created_at`,`ls_order`.`sn` AS `sn`,`ls_order`.`distance` AS `distance`,`ls_order`.`duration` AS `duration`,`ls_order`.`order_type` AS `order_type`,`ls_driver_account`.`amount` AS `fee` from (`ls_driver_account` join `ls_order`) where (`ls_driver_account`.`order_id` = `ls_order`.`id`);

-- ----------------------------
-- View structure for v_driver_take_cash
-- ----------------------------
DROP VIEW IF EXISTS `v_driver_take_cash`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_driver_take_cash` AS select `ls_driver_take_cash`.`id` AS `id`,`ls_driver_take_cash`.`driver_id` AS `driver_id`,`ls_driver_take_cash`.`amount` AS `amount`,`ls_driver_take_cash`.`bank_name` AS `bank_name`,`ls_driver_take_cash`.`bank_card` AS `bank_card`,`ls_driver_take_cash`.`status` AS `status`,`ls_driver_take_cash`.`created_at` AS `created_at`,`ls_driver_take_cash`.`updated_at` AS `updated_at`,`ls_driver`.`truename` AS `truename`,`ls_driver`.`phone` AS `phone`,`ls_driver`.`region_id` AS `region_id`,`ls_driver`.`company_id` AS `company_id`,`ls_driver`.`company_name` AS `company_name`,`ls_driver_take_cash`.`remark` AS `remark` from (`ls_driver` join `ls_driver_take_cash`) where (`ls_driver`.`id` = `ls_driver_take_cash`.`driver_id`) order by `ls_driver_take_cash`.`updated_at`;

-- ----------------------------
-- View structure for v_order
-- ----------------------------
DROP VIEW IF EXISTS `v_order`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_order` AS select `a`.`id` AS `id`,`a`.`sn` AS `sn`,`a`.`region_id` AS `region_id`,`a`.`customer_id` AS `customer_id`,`a`.`start_location` AS `start_location`,`a`.`start_latlng` AS `start_latlng`,`a`.`end_location` AS `end_location`,`a`.`end_latlng` AS `end_latlng`,`a`.`distance` AS `distance`,`a`.`duration` AS `duration`,`a`.`cost` AS `cost`,`a`.`tolls` AS `tolls`,`a`.`order_time` AS `order_time`,`a`.`up_time` AS `up_time`,`a`.`down_time` AS `down_time`,`a`.`driver_id` AS `driver_id`,`a`.`waiting_time` AS `waiting_time`,`a`.`accept_time` AS `accept_time`,`a`.`total_fee` AS `total_fee`,`a`.`pay_type` AS `pay_type`,`a`.`invoice` AS `invoice`,`a`.`status` AS `status`,`a`.`order_type` AS `order_type`,`a`.`is_dispatch` AS `is_dispatch`,`a`.`driver_commission` AS `driver_commission`,`a`.`created_at` AS `created_at`,`a`.`updated_at` AS `updated_at`,`a`.`find_num` AS `find_num`,`a`.`customer_phone` AS `customer_phone`,`a`.`driver_name` AS `driver_name`,`a`.`driver_phone` AS `driver_phone`,`a`.`car_no` AS `car_no`,`b`.`order_id` AS `order_id`,`b`.`start_fee` AS `start_fee`,`b`.`start_mileage` AS `start_mileage`,`b`.`mileage_fee_per_km` AS `mileage_fee_per_km`,`b`.`extra_mileage` AS `extra_mileage`,`b`.`duration_fee_per_minute` AS `duration_fee_per_minute`,`b`.`extra_duration_minutes` AS `extra_duration_minutes`,`b`.`long_distance_fee` AS `long_distance_fee`,`b`.`long_distance_trigger_mileage` AS `long_distance_trigger_mileage`,`b`.`temporary_surcharge` AS `temporary_surcharge`,`b`.`temporary_coefficent` AS `temporary_coefficent`,`b`.`insurance_id` AS `insurance_id`,`b`.`insurance_fee` AS `insurance_fee`,`b`.`coupon_id` AS `coupon_id`,`b`.`coupon_name` AS `coupon_name`,`a`.`add_price` AS `add_price`,`a`.`pay_amount` AS `pay_amount`,`a`.`real_pay_amount` AS `real_pay_amount`,`a`.`discount_amount` AS `discount_amount`,`a`.`commission_settle` AS `commission_settle`,`a`.`customer_token` AS `customer_token`,`a`.`company_id` AS `company_id` from (`ls_order` `a` join `ls_order_fee_details` `b`) where (`a`.`id` = `b`.`order_id`);

-- ----------------------------
-- View structure for v_user_coupon
-- ----------------------------
DROP VIEW IF EXISTS `v_user_coupon`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_user_coupon` AS select `ls_coupons_list`.`id` AS `id`,`ls_coupons_list`.`utype` AS `utype`,`ls_coupons_list`.`uid` AS `uid`,`ls_coupons_list`.`phone` AS `phone`,`ls_coupons_list`.`truename` AS `truename`,`ls_coupons_list`.`coupon_id` AS `coupon_id`,`ls_coupons_list`.`status` AS `status`,`ls_coupons_list`.`created_at` AS `created_at`,`ls_coupons_list`.`updated_at` AS `updated_at`,`ls_coupons_list`.`take_code` AS `take_code`,`ls_coupons`.`name` AS `name`,`ls_coupons`.`type` AS `type`,`ls_coupons`.`code` AS `code`,`ls_coupons`.`valid_type` AS `valid_type`,`ls_coupons`.`start_date` AS `start_date`,`ls_coupons`.`end_date` AS `end_date`,`ls_coupons`.`valid_days` AS `valid_days`,`ls_coupons`.`description` AS `description`,`ls_coupons`.`amount` AS `amount`,`ls_coupons`.`condition_amount` AS `condition_amount`,`ls_coupons`.`status` AS `coupon_status` from (`ls_coupons` join `ls_coupons_list`);

SET FOREIGN_KEY_CHECKS = 1;
