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
-- Table structure for table `dashboard_projects`
--

DROP TABLE IF EXISTS `dashboard_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_projects` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` longtext NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `status` varchar(50) NOT NULL,
  `department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `dashboard_projects_department_id_e88ff925_fk_dashboard` (`department_id`),
  CONSTRAINT `dashboard_projects_department_id_e88ff925_fk_dashboard` FOREIGN KEY (`department_id`) REFERENCES `dashboard_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard_projects`
--

LOCK TABLES `dashboard_projects` WRITE;
/*!40000 ALTER TABLE `dashboard_projects` DISABLE KEYS */;
INSERT INTO `dashboard_projects` VALUES (1,'IPTV','impliment the payment gateway','2025-05-29','2025-05-31','ongoing',NULL),(2,'Bitstorm Portfolio','abc','2025-05-20','2025-05-30','completed',NULL),(3,'AI Virtual Stylist','Client Brief:\r\n\"We need an AI-powered virtual stylist for our fashion e-commerce platform. The AI should recommend outfits based on user preferences, body type, weather, and occasion. It should learn from user behavior and give personalized clothing suggestions.\"\r\n\r\nKey Features:\r\n\r\nStyle preference quiz\r\n\r\nMachine learning recommendations\r\n\r\nIntegration with product inventory\r\n\r\nWeather-based outfit suggestions\r\n\r\n','2025-05-29','2026-01-29','ongoing',2),(4,'Real-Time Object Detection for Retail Stores','Client Brief:\r\n\"Our retail stores need an AI system that uses camera feeds to detect products being picked up or taken. It should help us track product interaction, theft prevention, and customer interest in real-time.\"\r\n\r\nKey Features:\r\n\r\nComputer vision for object detection\r\n\r\nReal-time video processing\r\n\r\nHeatmaps of customer engagement\r\n\r\nAlert system for unpurchased removals','2025-05-29','2026-01-29','completed',2),(5,'Uber','ANY','2025-05-29','2025-06-07','ongoing',3),(6,'uber2','uber2','2025-06-03','2025-06-03','completed',2),(7,'any new project','123`','2025-06-26','2025-06-26','pending',6);
/*!40000 ALTER TABLE `dashboard_projects` ENABLE KEYS */;
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
