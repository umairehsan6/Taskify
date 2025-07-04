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
-- Table structure for table `dashboard_taskreadstatus`
--

DROP TABLE IF EXISTS `dashboard_taskreadstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_taskreadstatus` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `last_read_at` datetime(6) NOT NULL,
  `task_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dashboard_taskreadstatus_user_id_task_id_2c1245d5_uniq` (`user_id`,`task_id`),
  KEY `dashboard_taskreadstatus_task_id_def3dd9d_fk_dashboard_tasks_id` (`task_id`),
  CONSTRAINT `dashboard_taskreadstatus_task_id_def3dd9d_fk_dashboard_tasks_id` FOREIGN KEY (`task_id`) REFERENCES `dashboard_tasks` (`id`),
  CONSTRAINT `dashboard_taskreadstatus_user_id_b295b0dc_fk_users_signupuser_id` FOREIGN KEY (`user_id`) REFERENCES `users_signupuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard_taskreadstatus`
--

LOCK TABLES `dashboard_taskreadstatus` WRITE;
/*!40000 ALTER TABLE `dashboard_taskreadstatus` DISABLE KEYS */;
INSERT INTO `dashboard_taskreadstatus` VALUES (1,'2025-06-19 06:34:43.708280',32,5),(2,'2025-06-18 12:53:43.548188',31,5),(3,'2025-06-18 12:54:05.235151',31,4),(6,'2025-06-23 07:29:35.229952',33,4),(7,'2025-06-26 08:38:46.476422',33,5),(8,'2025-06-17 11:23:32.150812',28,5),(9,'2025-06-26 05:38:16.115234',54,5),(10,'2025-07-03 05:04:48.916655',70,5);
/*!40000 ALTER TABLE `dashboard_taskreadstatus` ENABLE KEYS */;
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
