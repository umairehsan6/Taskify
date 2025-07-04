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
-- Table structure for table `dashboard_companydetails`
--

DROP TABLE IF EXISTS `dashboard_companydetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_companydetails` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `company_logo` varchar(100) DEFAULT NULL,
  `company_name` varchar(100) DEFAULT NULL,
  `company_description` longtext,
  `company_phone` varchar(15) DEFAULT NULL,
  `company_email` varchar(254) DEFAULT NULL,
  `company_website` varchar(200) DEFAULT NULL,
  `company_address` longtext,
  `company_founded_date` date DEFAULT NULL,
  `company_social_media_links` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard_companydetails`
--

LOCK TABLES `dashboard_companydetails` WRITE;
/*!40000 ALTER TABLE `dashboard_companydetails` DISABLE KEYS */;
INSERT INTO `dashboard_companydetails` VALUES (1,'company_logo/bitstorm_logo_5.png','Bitstorm Solution','We specialize in transforming businesses with\r\nenterprise-grade software solutions tailored to\r\ntheir needs. With a legacy of technical excellence, a\r\nglobal team of experts, and a passion for\r\ninnovation, we help organizations thrive in an\r\never-evolving digital landscape.','03091671552','umairehsan59@gmail.com','https://bitstormsolutions.com/','Khan Hari, P.O Dugri Harian, Teh. Pasrur, District Sialkot','2025-06-10','{\"twitter\": \"https://bitstormsolutions.com/\", \"facebook\": \"https://bitstormsolutions.com/\", \"linkedin\": \"https://bitstormsolutions.com/\", \"instagram\": \"https://bitstormsolutions.com/\"}');
/*!40000 ALTER TABLE `dashboard_companydetails` ENABLE KEYS */;
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
