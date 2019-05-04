DROP DATABASE IF EXISTS test;
CREATE DATABASE test;

USE test;


DROP TABLE IF EXISTS `celery_tasksetmeta`;
CREATE TABLE `celery_tasksetmeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taskset_id` varchar(155) DEFAULT NULL,
  `result` blob,
  `date_done` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `taskset_id` (`taskset_id`)
);

DROP TABLE IF EXISTS `celery_taskmeta`;
CREATE TABLE `celery_taskmeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` varchar(155) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `result` blob,
  `date_done` datetime DEFAULT NULL,
  `traceback` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`)
);

DROP TABLE IF EXISTS `master_tasks`;
CREATE TABLE `master_tasks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip_address` varchar(45) NOT NULL,
  `start_port` int(11) NOT NULL,
  `end_port` int(11) NOT NULL,
  `subnet` varchar(45) NOT NULL,
  `task_type` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
);


DROP TABLE IF EXISTS `celery_tasks`;
CREATE TABLE `celery_tasks` (
  `task_id` text NOT NULL,
  `master_task_id` int(11) DEFAULT NULL
);