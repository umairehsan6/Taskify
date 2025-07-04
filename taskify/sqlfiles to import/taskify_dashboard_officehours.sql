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
-- Table structure for table `dashboard_officehours`
--

DROP TABLE IF EXISTS `dashboard_officehours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_officehours` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `day` varchar(10) NOT NULL,
  `start_time` time(6) NOT NULL,
  `end_time` time(6) NOT NULL,
  `break_start_time` time(6) DEFAULT NULL,
  `break_end_time` time(6) DEFAULT NULL,
  `is_working_day` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard_officehours`
--

LOCK TABLES `dashboard_officehours` WRITE;
/*!40000 ALTER TABLE `dashboard_officehours` DISABLE KEYS */;
INSERT INTO `dashboard_officehours` VALUES (1,'monday','09:30:00.000000','18:30:00.000000','16:05:00.000000','16:09:00.000000',1,1),(2,'tuesday','09:30:00.000000','18:30:00.000000','14:00:00.000000','15:00:00.000000',1,1),(3,'wednesday','09:30:00.000000','18:30:00.000000','14:00:00.000000','15:00:00.000000',1,1),(4,'thursday','09:30:00.000000','18:30:00.000000','14:00:00.000000','15:13:00.000000',1,1),(5,'friday','09:30:00.000000','18:30:00.000000','14:00:00.000000','15:00:00.000000',1,1),(6,'saturday','09:30:00.000000','18:30:00.000000','14:00:00.000000','15:00:00.000000',0,1),(7,'sunday','09:30:00.000000','18:30:00.000000','14:00:00.000000','15:00:00.000000',0,1);
/*!40000 ALTER TABLE `dashboard_officehours` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-03 11:19:47
