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
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-05-29 11:04:50.969377'),(2,'auth','0001_initial','2025-05-29 11:04:52.781787'),(3,'admin','0001_initial','2025-05-29 11:04:53.155755'),(4,'admin','0002_logentry_remove_auto_add','2025-05-29 11:04:53.177528'),(5,'admin','0003_logentry_add_action_flag_choices','2025-05-29 11:04:53.223213'),(6,'contenttypes','0002_remove_content_type_name','2025-05-29 11:04:53.534457'),(7,'auth','0002_alter_permission_name_max_length','2025-05-29 11:04:53.678117'),(8,'auth','0003_alter_user_email_max_length','2025-05-29 11:04:53.739475'),(9,'auth','0004_alter_user_username_opts','2025-05-29 11:04:53.756162'),(10,'auth','0005_alter_user_last_login_null','2025-05-29 11:04:53.898190'),(11,'auth','0006_require_contenttypes_0002','2025-05-29 11:04:53.903688'),(12,'auth','0007_alter_validators_add_error_messages','2025-05-29 11:04:53.928170'),(13,'auth','0008_alter_user_username_max_length','2025-05-29 11:04:54.098194'),(14,'auth','0009_alter_user_last_name_max_length','2025-05-29 11:04:54.377189'),(15,'auth','0010_alter_group_name_max_length','2025-05-29 11:04:54.468351'),(16,'auth','0011_update_proxy_permissions','2025-05-29 11:04:54.507193'),(17,'auth','0012_alter_user_first_name_max_length','2025-05-29 11:04:54.671294'),(18,'users','0001_initial','2025-05-29 11:04:54.963266'),(19,'dashboard','0001_initial','2025-05-29 11:04:55.387936'),(20,'sessions','0001_initial','2025-05-29 11:04:55.549317'),(21,'dashboard','0002_projects','2025-05-29 11:24:52.085660'),(22,'dashboard','0003_officehours_tasks_taskactivitylog','2025-05-29 11:58:11.458966'),(23,'dashboard','0004_tasks_submitted_on','2025-06-02 07:47:13.719667'),(24,'dashboard','0005_tasks_expected_time','2025-06-04 04:44:09.749244'),(25,'users','0002_alter_signupuser_role','2025-06-04 07:21:22.645933'),(26,'dashboard','0006_companydetails','2025-06-10 05:31:33.580342'),(27,'dashboard','0007_remove_companydetails_company_ceo','2025-06-10 05:37:57.873925'),(28,'dashboard','0008_alter_companydetails_options','2025-06-10 07:09:49.587316'),(29,'dashboard','0009_employeeprofile','2025-06-10 10:15:40.912355'),(30,'dashboard','0010_chatmessage','2025-06-12 06:13:58.059693'),(31,'dashboard','0011_taskreadstatus','2025-06-16 10:53:31.540688'),(32,'dashboard','0012_alter_taskreadstatus_last_read_at','2025-06-17 13:24:32.198319'),(33,'dashboard','0013_notification','2025-06-30 07:59:12.759668');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
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
