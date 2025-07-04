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
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add signup user',7,'add_signupuser'),(26,'Can change signup user',7,'change_signupuser'),(27,'Can delete signup user',7,'delete_signupuser'),(28,'Can view signup user',7,'view_signupuser'),(29,'Can add user verification',8,'add_userverification'),(30,'Can change user verification',8,'change_userverification'),(31,'Can delete user verification',8,'delete_userverification'),(32,'Can view user verification',8,'view_userverification'),(33,'Can add department',9,'add_department'),(34,'Can change department',9,'change_department'),(35,'Can delete department',9,'delete_department'),(36,'Can view department',9,'view_department'),(37,'Can add user department',10,'add_userdepartment'),(38,'Can change user department',10,'change_userdepartment'),(39,'Can delete user department',10,'delete_userdepartment'),(40,'Can view user department',10,'view_userdepartment'),(41,'Can add projects',11,'add_projects'),(42,'Can change projects',11,'change_projects'),(43,'Can delete projects',11,'delete_projects'),(44,'Can view projects',11,'view_projects'),(45,'Can add office hours',12,'add_officehours'),(46,'Can change office hours',12,'change_officehours'),(47,'Can delete office hours',12,'delete_officehours'),(48,'Can view office hours',12,'view_officehours'),(49,'Can add task activity log',13,'add_taskactivitylog'),(50,'Can change task activity log',13,'change_taskactivitylog'),(51,'Can delete task activity log',13,'delete_taskactivitylog'),(52,'Can view task activity log',13,'view_taskactivitylog'),(53,'Can add tasks',14,'add_tasks'),(54,'Can change tasks',14,'change_tasks'),(55,'Can delete tasks',14,'delete_tasks'),(56,'Can view tasks',14,'view_tasks'),(57,'Can add company details',15,'add_companydetails'),(58,'Can change company details',15,'change_companydetails'),(59,'Can delete company details',15,'delete_companydetails'),(60,'Can view company details',15,'view_companydetails'),(61,'Can add employee profile',16,'add_employeeprofile'),(62,'Can change employee profile',16,'change_employeeprofile'),(63,'Can delete employee profile',16,'delete_employeeprofile'),(64,'Can view employee profile',16,'view_employeeprofile'),(65,'Can add chat message',17,'add_chatmessage'),(66,'Can change chat message',17,'change_chatmessage'),(67,'Can delete chat message',17,'delete_chatmessage'),(68,'Can view chat message',17,'view_chatmessage'),(69,'Can add task read status',18,'add_taskreadstatus'),(70,'Can change task read status',18,'change_taskreadstatus'),(71,'Can delete task read status',18,'delete_taskreadstatus'),(72,'Can view task read status',18,'view_taskreadstatus'),(73,'Can add notification',19,'add_notification'),(74,'Can change notification',19,'change_notification'),(75,'Can delete notification',19,'delete_notification'),(76,'Can view notification',19,'view_notification');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
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
