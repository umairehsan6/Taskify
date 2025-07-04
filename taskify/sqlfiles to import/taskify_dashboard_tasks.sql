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
-- Table structure for table `dashboard_tasks`
--

DROP TABLE IF EXISTS `dashboard_tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_tasks` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `task_name` varchar(50) NOT NULL,
  `task_description` longtext NOT NULL,
  `due_date` date DEFAULT NULL,
  `priority` varchar(10) NOT NULL,
  `status` varchar(50) NOT NULL,
  `task_file` varchar(100) DEFAULT NULL,
  `report` varchar(1000) DEFAULT NULL,
  `assigned_from_id` bigint DEFAULT NULL,
  `assigned_to_id` bigint DEFAULT NULL,
  `project_id` bigint DEFAULT NULL,
  `submitted_on` datetime(6) DEFAULT NULL,
  `expected_time` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_tasks_assigned_from_id_651f5b56_fk_users_signupuser_id` (`assigned_from_id`),
  KEY `dashboard_tasks_assigned_to_id_73b12b22_fk_dashboard` (`assigned_to_id`),
  KEY `dashboard_tasks_project_id_df597cd3_fk_dashboard_projects_id` (`project_id`),
  CONSTRAINT `dashboard_tasks_assigned_from_id_651f5b56_fk_users_signupuser_id` FOREIGN KEY (`assigned_from_id`) REFERENCES `users_signupuser` (`id`),
  CONSTRAINT `dashboard_tasks_assigned_to_id_73b12b22_fk_dashboard` FOREIGN KEY (`assigned_to_id`) REFERENCES `dashboard_userdepartment` (`id`),
  CONSTRAINT `dashboard_tasks_project_id_df597cd3_fk_dashboard_projects_id` FOREIGN KEY (`project_id`) REFERENCES `dashboard_projects` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard_tasks`
--

LOCK TABLES `dashboard_tasks` WRITE;
/*!40000 ALTER TABLE `dashboard_tasks` DISABLE KEYS */;
INSERT INTO `dashboard_tasks` VALUES (3,'BUGS','ANY','2025-06-06','high','on_hold','',NULL,6,6,5,NULL,NULL),(19,'test','test','2025-06-03','low','completed','',NULL,6,7,3,'2025-06-03 10:16:08.000000',10800000000),(20,'test uber','test','2025-06-03','medium','pending','',NULL,6,7,3,NULL,NULL),(21,'abc','abc','2025-06-03','medium','pending','',NULL,6,7,4,NULL,NULL),(22,'Chart check','CHart Check','2025-06-03','medium','completed','',NULL,6,3,3,'2025-06-04 05:55:20.071333',NULL),(23,'Test task for team lead','Test task','2025-06-04','medium','completed','task_files/bitstorm_logo_1.png','Thats the submitted report\r\n',5,4,3,'2025-06-11 06:31:53.419432',7200000000),(24,'Expected Time','Test','2025-06-05','low','completed','task_files/bitstorm_logo.png','report',4,3,3,'2025-06-11 05:15:20.863381',10800000000),(26,'Testing','a','2025-06-05','low','pending','',NULL,9,7,3,NULL,3660000000),(27,'Research On previous Code Base','FInd where api\'s are being placed what can be the causes of api glitches','2025-06-12','medium','completed','',NULL,5,4,6,'2025-06-11 11:03:54.102246',14400000000),(28,'Testing','testing','2025-06-25','low','completed','task_files/rayyan-amwDFa9qZ-k-unsplash_1.jpg',NULL,5,4,6,'2025-06-11 11:48:38.789064',10800000000),(29,'TEsT','any','2025-06-11','low','completed','',NULL,5,4,6,'2025-06-11 13:24:54.974219',1800000000),(30,'Testing','Testing','2025-06-11','low','completed','',NULL,4,3,3,'2025-06-27 12:31:53.398029',2400000000),(31,'testing','Api testing','2025-06-12','low','completed','',NULL,5,3,3,NULL,3540000000),(32,'teamlead test task','test task ','2025-06-15','high','completed','',NULL,5,4,3,'2025-06-20 06:58:07.597153',14400000000),(33,'Chat check','chat check','2025-06-17','low','completed','',NULL,5,3,3,NULL,7200000000),(34,'AJAx TEsting','Testing','2025-06-26','low','pending','',NULL,5,7,3,NULL,7200000000),(35,'AJAx TEsting','Testing','2025-06-26','low','pending','',NULL,5,7,3,NULL,7200000000),(36,'hjce','jeh','2025-06-19','low','pending','',NULL,5,7,3,NULL,82920000000),(37,'Team','kjbc','2025-06-19','medium','completed','task_files/IMG-20250516-WA0008_E9NmiKf.jpg',NULL,5,4,3,'2025-06-27 12:43:45.706842',10920000000),(38,'any','h','2025-06-19','low','pending','',NULL,5,7,3,NULL,300000000),(39,'check','check','2025-06-19','high','pending','',NULL,5,7,6,NULL,120000000),(40,'hello','hi','2025-06-20','medium','completed','',NULL,5,4,3,'2025-06-20 07:12:22.863999',14520000000),(41,'hello','description','2025-06-20','medium','pending','',NULL,5,6,3,NULL,14400000000),(43,'Testing','hi','2025-06-19','low','pending','',NULL,5,7,3,NULL,18000000000),(44,'teamlead','description','2025-06-19','low','completed','',NULL,5,4,3,'2025-06-20 07:12:31.798050',18000000000),(49,'Polling check again','polling check again','2025-06-26','high','completed','',NULL,5,4,6,'2025-06-20 07:01:15.131101',14400000000),(50,'Polling check again 321','Hello','2025-06-20','medium','completed','',NULL,5,4,3,'2025-06-20 07:01:12.755144',10800000000),(51,'polling check 431','Polling check ','2025-06-20','high','completed','',NULL,5,4,6,'2025-06-20 07:01:09.183017',14400000000),(52,'Tasks Check','tasks are changing','2025-06-21','low','completed','task_files/emp-dash.html','task 52',5,4,3,'2025-06-27 12:43:05.326009',10800000000),(53,'Waiting for Approval','waiting for approval','2025-06-27','high','completed','',NULL,4,3,3,'2025-06-27 12:24:49.000000',19800000000),(54,'ajax','ajax test','2025-06-20','high','completed','task_files/Umair_CV.pdf','new report2',5,4,3,'2025-06-27 12:38:18.417191',18000000000),(55,'ajax check again','Hello again','2025-06-20','high','completed','',NULL,5,4,3,NULL,18000000000),(56,'hi','any','2025-06-20','high','completed','',NULL,5,4,3,'2025-06-27 12:23:36.000000',18000000000),(57,'pending tasks check','noted','2025-06-24','medium','completed','',NULL,5,4,3,'2025-06-27 12:24:12.000000',14400000000),(60,'approval buttons condition check','123','2025-07-10','high','completed','',NULL,4,3,3,'2025-06-27 12:22:42.000000',7200000000),(62,'check','cjeiv','2025-06-27','low','completed','',NULL,5,4,3,'2025-06-27 12:40:55.348374',3660000000),(63,'salksdn','ldjfn','2025-06-27','low','completed','',NULL,5,4,3,'2025-06-27 12:47:44.250219',116580000000),(64,'jdbc','kdjbc','2025-06-27','low','completed','',NULL,5,4,3,'2025-06-27 12:51:51.040434',3720000000),(65,'djhc','kdjbc','2025-06-27','medium','completed','',NULL,5,4,3,'2025-06-27 12:54:06.205328',3660000000),(66,'1','1','2025-06-27','low','completed','',NULL,5,4,3,'2025-06-27 12:57:57.532043',3660000000),(67,'12','12','2025-06-27','low','completed','',NULL,5,4,3,'2025-06-27 12:59:45.502642',3660000000),(68,'jeibf','kejbfw','2025-06-27','low','completed','',NULL,5,4,3,'2025-06-27 13:03:10.337859',3660000000),(69,'check','123','2025-06-27','low','pending','',NULL,5,4,3,NULL,36600000000),(70,'testing','123321','2025-06-27','high','on_hold','',NULL,5,4,3,NULL,46800000000),(71,'Api testing','12345','2025-06-27','medium','completed','',NULL,5,4,3,'2025-07-01 05:23:06.610674',32400000000),(72,'Approval Pending','check ','2025-06-30','low','pending','',NULL,4,3,3,NULL,21960000000),(73,'check ','1111','2025-06-30','low','completed','',NULL,5,3,3,'2025-07-01 05:48:59.565936',7260000000),(74,'creayte ','leknd','2025-06-30','low','completed','',NULL,4,3,3,'2025-07-01 05:33:42.519613',3660000000),(75,'creayte ','leknd','2025-06-30','low','completed','',NULL,4,3,3,'2025-07-01 05:26:22.158688',3660000000),(76,'creayte ','leknd','2025-06-30','low','completed','',NULL,4,3,3,'2025-07-01 05:25:50.161582',3660000000),(77,'employee','2ued`','2025-06-30','low','pending','',NULL,5,4,3,NULL,44460000000),(78,'notification check ','2','2025-06-30','low','on_hold','',NULL,4,3,3,NULL,83520000000),(81,'notification for teamlead','feoi','2025-06-30','low','completed','',NULL,4,3,3,'2025-07-01 05:39:19.457628',76860000000),(82,'jdbc ','je c','2025-06-30','low','completed','',NULL,5,3,3,'2025-07-01 05:36:52.224924',4860000000),(86,'kjvb','NEFOBIU','2025-06-30','low','completed','',NULL,4,3,3,'2025-07-01 05:34:27.275183',76320000000),(88,'test','any','2025-07-08','low','on_hold','',NULL,4,3,3,NULL,43920000000),(90,'ksj','j','2025-07-01','low','completed','',NULL,5,3,3,'2025-07-01 05:51:34.071506',44460000000),(92,'lkejnf','jdbefw','2025-07-01','low','pending','',NULL,5,3,3,NULL,44580000000);
/*!40000 ALTER TABLE `dashboard_tasks` ENABLE KEYS */;
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
