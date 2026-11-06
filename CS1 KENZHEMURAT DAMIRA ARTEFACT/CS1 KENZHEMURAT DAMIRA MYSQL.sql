CREATE DATABASE  IF NOT EXISTS `school_management_sw2026` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `school_management_sw2026`;
-- MySQL dump 10.13  Distrib 8.0.45, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: school_management_sw2026
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `attendance_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_id` int NOT NULL,
  `attendance_date` date NOT NULL DEFAULT (curdate()),
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`attendance_id`),
  KEY `fk_attendance_student` (`student_id`),
  KEY `fk_attendance_course` (`course_id`),
  CONSTRAINT `fk_attendance_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attendance_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `attendance_chk_1` CHECK ((`status` in (_utf8mb4'Present',_utf8mb4'Absent',_utf8mb4'Late')))
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,1,1,'2026-05-11','Present'),(2,1,3,'2026-05-12','Present'),(3,2,1,'2026-05-11','Absent'),(4,2,2,'2026-05-13','Late'),(5,3,1,'2026-05-11','Present'),(6,3,4,'2026-05-14','Present'),(7,4,3,'2026-05-12','Late'),(8,4,5,'2026-05-15','Present'),(9,5,1,'2026-05-11','Present'),(10,5,2,'2026-05-13','Absent'),(11,6,3,'2026-05-12','Present'),(12,6,4,'2026-05-14','Present'),(13,7,1,'2026-05-11','Late'),(14,7,5,'2026-05-15','Present'),(15,8,2,'2026-05-13','Present'),(16,8,3,'2026-05-12','Absent'),(17,9,4,'2026-05-14','Present'),(18,9,5,'2026-05-15','Present'),(19,10,1,'2026-05-11','Present'),(20,10,3,'2026-05-12','Late');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `course_name` varchar(100) NOT NULL,
  `course_code` varchar(20) NOT NULL,
  `teacher_id` int NOT NULL,
  `course_credits` int NOT NULL,
  PRIMARY KEY (`course_id`),
  UNIQUE KEY `course_code` (`course_code`),
  KEY `fk_course_teacher` (`teacher_id`),
  CONSTRAINT `fk_course_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `courses_chk_1` CHECK ((`course_credits` between 1 and 10))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (1,'Mathematics','MATH101',1,5),(2,'History','HIST101',2,3),(3,'English','ENGL101',3,4),(4,'Physics','PHYS101',4,4),(5,'Biology','BIOL101',5,3);
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grades`
--

DROP TABLE IF EXISTS `grades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades` (
  `grade_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_id` int NOT NULL,
  `grade_value` varchar(5) NOT NULL,
  `grade_date` date NOT NULL DEFAULT (curdate()),
  PRIMARY KEY (`grade_id`),
  KEY `fk_grade_student` (`student_id`),
  KEY `fk_grade_course` (`course_id`),
  CONSTRAINT `fk_grade_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_grade_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `grades_chk_1` CHECK ((`grade_value` in (_utf8mb4'A',_utf8mb4'B',_utf8mb4'C',_utf8mb4'D',_utf8mb4'F')))
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades`
--

LOCK TABLES `grades` WRITE;
/*!40000 ALTER TABLE `grades` DISABLE KEYS */;
INSERT INTO `grades` VALUES (1,1,1,'A','2026-05-11'),(2,1,3,'B','2026-05-12'),(3,2,1,'C','2026-05-11'),(4,2,2,'B','2026-05-13'),(5,3,1,'A','2026-05-11'),(6,3,4,'B','2026-05-14'),(7,4,3,'A','2026-05-12'),(8,4,5,'C','2026-05-15'),(9,5,1,'B','2026-05-11'),(10,5,2,'D','2026-05-13'),(11,6,3,'A','2026-05-12'),(12,6,4,'B','2026-05-14'),(13,7,1,'C','2026-05-11'),(14,7,5,'A','2026-05-15'),(15,8,2,'B','2026-05-13'),(16,8,3,'C','2026-05-12'),(17,9,4,'A','2026-05-14'),(18,9,5,'B','2026-05-15'),(19,10,1,'A','2026-05-11'),(20,10,3,'B','2026-05-12');
/*!40000 ALTER TABLE `grades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registrations`
--

DROP TABLE IF EXISTS `registrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registrations` (
  `registration_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_id` int NOT NULL,
  `registration_date` date NOT NULL DEFAULT (curdate()),
  PRIMARY KEY (`registration_id`),
  KEY `fk_registration_student` (`student_id`),
  KEY `fk_registration_course` (`course_id`),
  CONSTRAINT `fk_registration_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_registration_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registrations`
--

LOCK TABLES `registrations` WRITE;
/*!40000 ALTER TABLE `registrations` DISABLE KEYS */;
INSERT INTO `registrations` VALUES (1,1,1,'2026-01-10'),(2,1,3,'2026-01-10'),(3,2,1,'2026-01-10'),(4,2,2,'2026-01-10'),(5,3,1,'2026-01-11'),(6,3,4,'2026-01-11'),(7,4,3,'2026-01-11'),(8,4,5,'2026-01-11'),(9,5,1,'2026-01-12'),(10,5,2,'2026-01-12'),(11,6,3,'2026-01-12'),(12,6,4,'2026-01-12'),(13,7,1,'2026-01-13'),(14,7,5,'2026-01-13'),(15,8,2,'2026-01-13'),(16,8,3,'2026-01-13'),(17,9,4,'2026-01-14'),(18,9,5,'2026-01-14'),(19,10,1,'2026-01-14'),(20,10,3,'2026-01-14');
/*!40000 ALTER TABLE `registrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `student_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` varchar(10) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `address` varchar(255) NOT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `students_chk_1` CHECK ((`gender` in (_utf8mb4'Male',_utf8mb4'Female',_utf8mb4'Other')))
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,'Amina','Kovaleva','2008-03-15','Female','amina.kovaleva@school.kz','+77011110001','Almaty, Abay 10'),(2,'Dias','Nurlan','2007-07-22','Male','dias.nurlan@school.kz','+77011110002','Almaty, Dostyk 5'),(3,'Arman','Zhaksylyk','2008-01-10','Male','arman.zhaksylyk@school.kz','+77011110003','Astana, Kerey 3'),(4,'Sofia','Petrova','2007-11-30','Female','sofia.petrova@school.kz','+77011110004','Astana, Mangilik 7'),(5,'Miras','Aitbay','2008-05-18','Male','miras.aitbay@school.kz','+77011110005','Almaty, Seifullin 12'),(6,'Alina','Sadykova','2007-09-04','Female','alina.sadykova@school.kz','+77011110006','Almaty, Furmanov 8'),(7,'Ruslan','Imanov','2008-02-27','Male','ruslan.imanov@school.kz','+77011110007','Astana, Beibitshilik 2'),(8,'Leila','Karimova','2007-12-05','Female','leila.karimova@school.kz','+77011110008','Almaty, Tole Bi 15'),(9,'Sanzhar','Mukhanov','2008-06-14','Male','sanzhar.mukhanov@school.kz','+77011110009','Astana, Kabanbay 4'),(10,'Kamila','Aubakirova','2007-08-20','Female','kamila.aubakirova@school.kz','+77011110010','Almaty, Al-Farabi 9'),(11,'Amina','Sabyr','2008-08-08','Female','aminas@school.kz','87068789562','Sauran, 98');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `teacher_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `department` varchar(100) NOT NULL,
  PRIMARY KEY (`teacher_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES (1,'Dana','Sarsen','dana.sarsen@school.kz','+77011112233','Mathematics'),(2,'Timur','Omarov','timur.omarov@school.kz','+77022223344','History'),(3,'Aliya','Nurgalieva','aliya.nurgalieva@school.kz','+77033334455','English'),(4,'Erlan','Kassymov','erlan.kassymov@school.kz','+77044445566','Physics'),(5,'Saltanat','Akhmetova','saltanat.akhmetova@school.kz','+77055556677','Biology');
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-27 10:42:16
