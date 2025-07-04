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
-- Table structure for table `dashboard_employeeprofile`
--

DROP TABLE IF EXISTS `dashboard_employeeprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_employeeprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `profile_picture` varchar(100) DEFAULT NULL,
  `bio` longtext,
  `contact_number` varchar(15) DEFAULT NULL,
  `address` longtext,
  `date_of_birth` date DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_employeepr_user_id_13f47d23_fk_users_sig` (`user_id`),
  CONSTRAINT `dashboard_employeepr_user_id_13f47d23_fk_users_sig` FOREIGN KEY (`user_id`) REFERENCES `users_signupuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard_employeeprofile`
--

LOCK TABLES `dashboard_employeeprofile` WRITE;
/*!40000 ALTER TABLE `dashboard_employeeprofile` DISABLE KEYS */;
INSERT INTO `dashboard_employeeprofile` VALUES (1,'profile_pictures/hassan-sherif--rFtjorcz2Q-unsplash.jpg','Error','0315-0000000','Chawinda','2002-07-20',4),(2,'profile_pictures/hobijist3d-Auw1Cqsawtg-unsplash.jpg','No Lies','0315-0000000','Gujrawala','2025-06-10',5),(3,'',NULL,NULL,NULL,NULL,6),(4,'',NULL,NULL,NULL,NULL,9),(5,'',NULL,NULL,NULL,NULL,8);
/*!40000 ALTER TABLE `dashboard_employeeprofile` ENABLE KEYS */;
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
