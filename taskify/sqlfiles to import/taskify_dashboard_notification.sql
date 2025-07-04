-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: taskify
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dashboard_notification`
--

DROP TABLE IF EXISTS `dashboard_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_notification` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message` longtext NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_notification_user_id_e4f6848c_fk_users_signupuser_id` (`user_id`),
  CONSTRAINT `dashboard_notification_user_id_e4f6848c_fk_users_signupuser_id` FOREIGN KEY (`user_id`) REFERENCES `users_signupuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard_notification`
--

LOCK TABLES `dashboard_notification` WRITE;
/*!40000 ALTER TABLE `dashboard_notification` DISABLE KEYS */;
INSERT INTO `dashboard_notification` VALUES (1,'You recieved a new task named From Teamlead','2025-06-30 08:05:00.101308',1,4),(2,'new notification for employee','2025-06-30 08:23:08.979157',1,4),(3,'check notification','2025-06-30 08:25:50.154480',1,4),(4,'You have been assigned a new task: check  by teamlead','2025-06-30 10:40:34.287772',1,4),(5,'employee requested approval for a new task: creayte . Available to approve in the approval section.','2025-06-30 10:43:38.903664',0,1),(6,'employee requested approval for a new task: creayte . Available to approve in the approval section.','2025-06-30 10:43:38.920656',0,6),(7,'employee requested approval for a new task: creayte . Available to approve in the approval section.','2025-06-30 10:43:38.935670',0,7),(8,'employee requested approval for a new task: creayte . Available to approve in the approval section.','2025-06-30 10:43:38.949626',1,8),(9,'employee requested approval for a new task: notification check . Available to approve in the approval section.','2025-06-30 10:54:10.707843',0,7),(10,'employee requested approval for a new task: notification check . Available to approve in the approval section.','2025-06-30 10:54:10.715367',1,8),(11,'employee requested approval for a new task: invalid task . Available to approve in the approval section.','2025-06-30 11:00:32.351525',0,7),(12,'employee requested approval for a new task: invalid task . Available to approve in the approval section.','2025-06-30 11:00:32.362652',1,8),(13,'employee requested approval for a new task: notification for teamlead. Available to approve in the approval section.','2025-06-30 11:11:23.654146',1,5),(14,'You have been assigned a new task: jdbc  by teamlead','2025-06-30 11:15:01.193876',1,4),(15,'employee requested approval for a new task: ekjfb1. Available to approve in the approval section.','2025-06-30 11:18:09.396007',1,5),(16,'employee requested approval for a new task: jbk. Available to approve in the approval section.','2025-06-30 11:22:34.164692',1,5),(17,'employee requested approval for a new task: ejbv. Available to approve in the approval section.','2025-06-30 11:56:06.726245',1,5),(18,'employee requested approval for a new task: kjvb. Available to approve in the approval section.','2025-06-30 12:31:02.640800',1,5),(19,'employee requested approval for a new task: polling  check . Available to approve in the approval section.','2025-06-30 12:35:18.843505',1,5),(20,'Your task \'Approval Pending\' has been approved and is now pending.','2025-06-30 12:39:42.549255',1,4),(21,'Your task \'notification check \' has been approved and is now pending.','2025-06-30 12:39:45.239088',1,4),(22,'Your task \'invalid task \' has been approved and is now pending.','2025-06-30 12:39:46.260222',1,4),(23,'Your task \'ekjfb1\' has been approved and is now pending.','2025-06-30 12:40:31.595521',1,4),(24,'Your task \'jbk\' has been approved and is now pending.','2025-06-30 12:40:33.096488',1,4),(25,'Your task \'ejbv\' has been rejected and deleted by 6','2025-06-30 12:48:36.811522',1,4),(26,'Your task \'approval pending 2`\' has been rejected and deleted by admin','2025-06-30 12:50:16.160341',1,4),(27,'Your task \'notification for teamlead\' has been approved and is now pending.','2025-06-30 15:17:35.239245',1,4),(28,'Task \'Api testing\' status updated to Completed','2025-07-01 05:23:06.623675',1,5),(29,'Task \'Api testing\' status updated to Completed','2025-07-01 05:23:06.627676',0,6),(30,'Your task \'kjvb\' has been approved and is now pending.','2025-07-01 05:25:11.123194',1,4),(31,'Your task \'polling  check \' has been rejected and deleted by admin','2025-07-01 05:32:38.113173',1,4),(32,'employee requested approval for a new task: test. Available to approve in the approval section.','2025-07-01 05:37:39.470334',1,5),(33,'Your task \'test\' has been approved and is now pending.','2025-07-01 05:40:13.561422',1,4),(34,'employee requested approval for a new task: helo. Available to approve in the approval section.','2025-07-01 05:41:34.810223',1,5),(35,'You have been assigned a new task: ksj by teamlead','2025-07-01 05:44:28.185504',1,4),(36,'Task \'ksj\' from AI Virtual Stylist by employee has been updated to Completed now you can view reports and files','2025-07-01 05:51:34.085958',1,5),(37,'Task \'ksj\' from AI Virtual Stylist by employee has been updated to Completed now you can view reports and files','2025-07-01 05:51:34.089949',0,6),(38,'Your task \'helo\' has been rejected and deleted by admin','2025-07-01 08:57:59.150787',1,4),(39,'employee requested approval for a new task: jh v. Available to approve in the approval section.','2025-07-01 10:03:07.999795',1,5),(40,'You have been assigned a new task: lkejnf by teamlead','2025-07-01 11:51:19.870580',1,4),(41,'employee requested approval for a new task: jkdbKBH. Available to approve in the approval section.','2025-07-01 11:54:51.047287',1,5),(42,'employee requested approval for a new task: jhdHJV. Available to approve in the approval section.','2025-07-01 11:57:23.330560',1,5),(43,'employee requested approval for a new task: jdbh. Available to approve in the approval section.','2025-07-01 11:57:41.379930',1,5),(44,'employee requested approval for a new task: ih. Available to approve in the approval section.','2025-07-01 11:57:53.712128',1,5),(45,'employee requested approval for a new task: j. Available to approve in the approval section.','2025-07-01 11:58:13.277646',1,5),(46,'employee requested approval for a new task: ds. Available to approve in the approval section.','2025-07-01 11:58:44.031692',1,5),(47,'employee requested approval for a new task: 11. Available to approve in the approval section.','2025-07-01 12:01:21.565641',1,5),(48,'employee requested approval for a new task: jbn. Available to approve in the approval section.','2025-07-01 12:06:53.287873',1,5),(49,'employee requested approval for a new task: ln. Available to approve in the approval section.','2025-07-01 12:07:05.774593',1,5),(50,'employee requested approval for a new task: lfkn. Available to approve in the approval section.','2025-07-01 12:07:17.365301',1,5),(51,'employee requested approval for a new task: lfekn. Available to approve in the approval section.','2025-07-01 12:07:40.576810',1,5),(52,'Your task \'lfekn\' has been rejected and deleted by admin','2025-07-01 12:11:02.525682',1,4),(53,'Your task \'ln\' has been rejected and deleted by admin','2025-07-01 12:11:04.667921',1,4),(54,'Your task \'lfkn\' has been rejected and deleted by admin','2025-07-01 12:11:07.034944',1,4),(55,'Your task \'jbn\' has been rejected and deleted by admin','2025-07-01 12:11:09.628658',1,4),(56,'Your task \'11\' has been rejected and deleted by admin','2025-07-01 12:11:13.206549',1,4),(57,'Your task \'ds\' has been rejected and deleted by admin','2025-07-01 12:11:16.290996',1,4),(58,'Your task \'j\' has been rejected and deleted by admin','2025-07-01 12:11:19.574650',1,4),(59,'Your task \'ih\' has been rejected and deleted by admin','2025-07-01 12:11:22.359125',1,4),(60,'Your task \'jdbh\' has been rejected and deleted by admin','2025-07-01 12:27:54.258029',1,4),(61,'Your task \'jkdbKBH\' has been rejected and deleted by admin','2025-07-01 12:27:58.274924',1,4),(62,'Your task \'jh v\' has been rejected and deleted by admin','2025-07-01 12:28:04.715046',1,4),(63,'Your task \'jhdHJV\' has been rejected and deleted by admin','2025-07-01 12:28:10.121526',0,4),(64,'ekhb','2025-07-02 12:10:44.591963',1,5),(65,'kejbf','2025-07-02 12:11:08.390062',1,5);
/*!40000 ALTER TABLE `dashboard_notification` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-03 11:19:49
