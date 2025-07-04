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
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-05-29 11:16:05.371350','1','umairehsan6',2,'[{\"changed\": {\"fields\": [\"Role\"]}}]',7,1),(2,'2025-05-29 11:27:32.545028','1','Bitstorm',1,'[{\"added\": {}}]',9,1),(3,'2025-05-29 11:28:21.916569','1','IPTV',1,'[{\"added\": {}}]',11,1),(4,'2025-05-29 11:30:06.940108','1','umairehsan6 - Bitstorm',1,'[{\"added\": {}}]',10,1),(5,'2025-05-29 12:05:50.998110','3','1111',3,'',7,1),(6,'2025-05-29 12:05:50.998110','2','hamza',3,'',7,1),(7,'2025-06-03 05:46:39.521822','18','Activity log for Testing',2,'[{\"changed\": {\"fields\": [\"Duration\"]}}]',13,1),(8,'2025-06-03 05:52:24.062200','19','Activity log for Testing',3,'',13,1),(9,'2025-06-03 05:52:24.062200','18','Activity log for Testing',3,'',13,1),(10,'2025-06-03 05:52:24.062200','17','Activity log for Testing',3,'',13,1),(11,'2025-06-03 05:53:48.519061','16','Time Test - AI Virtual Stylist - admin',2,'[{\"changed\": {\"fields\": [\"Assigned from\"]}}]',14,1),(12,'2025-06-03 05:56:07.596837','16','Time Test - AI Virtual Stylist - teamlead',2,'[{\"changed\": {\"fields\": [\"Assigned to\", \"Assigned from\"]}}]',14,1),(13,'2025-06-03 07:22:51.693382','17','ON time test - AI Virtual Stylist - employee',2,'[{\"changed\": {\"fields\": [\"Assigned to\"]}}]',14,1),(14,'2025-06-03 11:09:55.267096','22','Chart check - AI Virtual Stylist - employee',1,'[{\"added\": {}}]',14,1),(15,'2025-06-03 11:10:37.870558','26','Activity log for Chart check',1,'[{\"added\": {}}]',13,1),(16,'2025-06-03 11:12:01.506695','26','Activity log for Chart check',2,'[{\"changed\": {\"fields\": [\"Duration\"]}}]',13,1),(17,'2025-06-03 11:12:17.458418','26','Activity log for Chart check',2,'[{\"changed\": {\"fields\": [\"Duration\"]}}]',13,1),(18,'2025-06-03 11:12:30.033398','25','Activity log for test',2,'[{\"changed\": {\"fields\": [\"Duration\"]}}]',13,1),(19,'2025-06-03 12:50:58.035536','14','Activity log for Bugs2',3,'',13,1),(20,'2025-06-04 05:19:49.016875','24','Expected Time - AI Virtual Stylist - employee',2,'[{\"changed\": {\"fields\": [\"Expected time\"]}}]',14,1),(21,'2025-06-04 05:20:07.317160','23','Test task for team lead - AI Virtual Stylist - teamlead',2,'[{\"changed\": {\"fields\": [\"Task name\", \"Task description\", \"Expected time\"]}}]',14,1),(22,'2025-06-04 05:20:52.391753','19','test - AI Virtual Stylist - umair',2,'[{\"changed\": {\"fields\": [\"Expected time\"]}}]',14,1),(23,'2025-06-04 05:20:59.213708','19','test - AI Virtual Stylist - umair',2,'[]',14,1),(24,'2025-06-04 05:21:05.670397','15','Expiring Today - AI Virtual Stylist - employee',2,'[{\"changed\": {\"fields\": [\"Task name\", \"Expected time\"]}}]',14,1),(25,'2025-06-04 05:21:25.021362','15','Expiring Today - AI Virtual Stylist - employee',2,'[{\"changed\": {\"fields\": [\"Expected time\"]}}]',14,1),(26,'2025-06-04 12:05:51.411671','26','Activity log for Chart check',2,'[{\"changed\": {\"fields\": [\"Duration\"]}}]',13,1),(27,'2025-06-10 06:40:13.401875','1','Company Details',3,'',15,1),(28,'2025-06-10 06:47:35.057981','2','Bitstorm Solution',1,'[{\"added\": {}}]',15,1),(29,'2025-06-10 07:09:09.800744','2','Bitstorm Solution',3,'',15,1),(30,'2025-06-12 05:27:31.339066','35','Activity log for Research On previous Code Base',3,'',13,1),(31,'2025-06-12 08:18:02.695899','1','umair - HEllo Socket check 1 , 2 , 3...',1,'[{\"added\": {}}]',17,1),(32,'2025-06-12 11:04:10.504726','2','manager - Thats a check message or comment appearing in task...',1,'[{\"added\": {}}]',17,1),(33,'2025-06-19 12:55:21.480395','48','ajax polling check 123 - AI Virtual Stylist - teamlead',3,'',14,1),(34,'2025-06-19 12:55:21.480395','47','Ajax polling check  - AI Virtual Stylist - teamlead',3,'',14,1),(35,'2025-06-19 12:55:21.480395','46','poling check 12 - AI Virtual Stylist - teamlead',3,'',14,1),(36,'2025-06-19 12:55:21.480395','45','polling h=check - AI Virtual Stylist - teamlead',3,'',14,1),(37,'2025-06-20 07:59:38.793176','54','ajax - AI Virtual Stylist - teamlead',2,'[{\"changed\": {\"fields\": [\"Task file\"]}}]',14,1),(38,'2025-06-20 08:00:04.997786','54','ajax - AI Virtual Stylist - teamlead',2,'[{\"changed\": {\"fields\": [\"Task file\"]}}]',14,1),(39,'2025-06-27 12:22:44.451142','60','approval buttons condition check - AI Virtual Stylist - employee',2,'[{\"changed\": {\"fields\": [\"Task name\", \"Submitted on\"]}}]',14,1),(40,'2025-06-27 12:23:37.971443','56','hi - AI Virtual Stylist - teamlead',2,'[{\"changed\": {\"fields\": [\"Submitted on\"]}}]',14,1),(41,'2025-06-27 12:24:17.722727','57','pending tasks check - AI Virtual Stylist - teamlead',2,'[{\"changed\": {\"fields\": [\"Task name\", \"Status\", \"Submitted on\"]}}]',14,1),(42,'2025-06-27 12:24:50.498403','53','Waiting for Approval - AI Virtual Stylist - employee',2,'[{\"changed\": {\"fields\": [\"Status\", \"Submitted on\"]}}]',14,1),(43,'2025-06-27 13:02:05.162950','107','Activity log for Tasks Check',3,'',13,1),(44,'2025-06-27 13:02:05.162950','103','Activity log for Waiting for Approval',3,'',13,1),(45,'2025-06-30 08:05:00.104310','1','Notification for employee - You recieved a new t... (Unread)',1,'[{\"added\": {}}]',19,1),(46,'2025-06-30 08:23:08.981151','2','Notification for employee - new notification for... (Unread)',1,'[{\"added\": {}}]',19,1),(47,'2025-06-30 08:25:50.156015','3','Notification for employee - check notification... (Unread)',1,'[{\"added\": {}}]',19,1),(48,'2025-07-01 13:10:52.533857','63','Notification for employee - Your task \'jhdHJV\' h... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(49,'2025-07-01 13:11:16.481159','62','Notification for employee - Your task \'jh v\' has... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(50,'2025-07-01 13:11:27.001362','61','Notification for employee - Your task \'jkdbKBH\' ... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(51,'2025-07-01 13:11:32.915693','60','Notification for employee - Your task \'jdbh\' has... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(52,'2025-07-01 13:12:49.750582','61','Notification for employee - Your task \'jkdbKBH\' ... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(53,'2025-07-01 13:12:59.148252','62','Notification for employee - Your task \'jh v\' has... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(54,'2025-07-01 13:13:06.908863','63','Notification for employee - Your task \'jhdHJV\' h... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(55,'2025-07-01 13:13:18.556107','60','Notification for employee - Your task \'jdbh\' has... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(56,'2025-07-02 05:02:14.052411','59','Notification for employee - Your task \'ih\' has b... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(57,'2025-07-02 05:02:18.632348','58','Notification for employee - Your task \'j\' has be... (Read)',2,'[]',19,1),(58,'2025-07-02 05:02:23.041416','57','Notification for employee - Your task \'ds\' has b... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(59,'2025-07-02 12:09:21.204879','63','Notification for employee - Your task \'jhdHJV\' h... (Unread)',2,'[{\"changed\": {\"fields\": [\"Is read\"]}}]',19,1),(60,'2025-07-02 12:10:44.617456','64','Notification for teamlead - ekhb... (Unread)',1,'[{\"added\": {}}]',19,1),(61,'2025-07-02 12:11:08.392111','65','Notification for teamlead - kejbf... (Unread)',1,'[{\"added\": {}}]',19,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-03 11:19:48
