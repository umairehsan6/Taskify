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
-- Table structure for table `users_signupuser`
--

DROP TABLE IF EXISTS `users_signupuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_signupuser` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(254) NOT NULL,
  `password` varchar(128) NOT NULL,
  `role` varchar(50) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_signupuser`
--

LOCK TABLES `users_signupuser` WRITE;
/*!40000 ALTER TABLE `users_signupuser` DISABLE KEYS */;
INSERT INTO `users_signupuser` VALUES (1,'Mian Umair Ehsan','Mian Ehsan Ullah','umairehsan6','umairehsan59@gmail.com','pbkdf2_sha256$870000$c1cofsAIS2XyQHqZQMomJa$GvJfFF0kJX1EK6/+HDEvuDHcJVpi+KyonhaamPj3K3s=','admin',1,1),(4,'employee','employee','employee','employee@gmail.com','pbkdf2_sha256$870000$XoIuAzU8LY5XzQ3jo6vuKj$kffyJUXuiFSCBt5k3vcZSCHWovZfQzBcd5H7dYMZb1g=','employee',1,0),(5,'teamlead','teamlead','teamlead','teamlead@gmail.com','pbkdf2_sha256$870000$paRpdBQlwFZeqYv2dxNztM$oN+8Q5xI89m88OBLxuRm+HwhxMKto/oFlGT01YRM8lQ=','teamlead',1,0),(6,'admin','admin','admin','admin@gmail.com','pbkdf2_sha256$870000$SsTPzsT5r19uID0iwzHvcq$jO0gXgCJNix68mcAJsOcdcCT3WOPzcXqhOwZCCPyu74=','admin',1,0),(7,'uberemployee','.','uber','uber@gmail.com','pbkdf2_sha256$870000$4LQ57x45kUMJP75dr9W8dW$XQbN05S9fsSzhlcpAUqswhiA9fe94W9d/L/OgIj+QCM=','teamlead',1,0),(8,'Umair','EHsan','umair','umair@gmail.com','pbkdf2_sha256$870000$0pnxnilc6GkZU1liYyW19c$z4/CL/HDi0xwGaaBt+vfWxWJ24VSdOTnnnnWIOskpeU=','teamlead',1,0),(9,'Manager','Bitstorm','manager','manager@gmail.com','pbkdf2_sha256$870000$wpih53rZnI09w53XU3yCYn$IN0iN8U2XvJEyPdduhSW4znG43O05C0EtyD6wvMynME=','manager',1,0),(10,'Mian Umair Ehsan','Mian Ehsan Ullah','talha','umair.ehsan.34@gmail.com','pbkdf2_sha256$870000$KvlYn3yHAtUngC7m8GvLHy$HYNBQ6UHRvdDzpBkq5WgwAihWgfA/aL4sNvj4ElOC9U=','employee',1,0),(11,'Farhan','Sajjad','farhan','farhansajjad006@gmail.com','pbkdf2_sha256$870000$la8Db54G2eIF7bFMIHB058$0RF/TF6iXwqKVtjLcP+wsJxtciIBGDuS0E5KVC7ahcM=','employee',1,0);
/*!40000 ALTER TABLE `users_signupuser` ENABLE KEYS */;
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
