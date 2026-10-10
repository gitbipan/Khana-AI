-- ====================================================================
-- Khana-AI MySQL Database Schema
-- Run this script on your hosted MySQL database instance
-- (AWS RDS, PlanetScale, Railway, Aiven, or local MySQL)
-- ====================================================================

CREATE DATABASE IF NOT EXISTS khana_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE khana_ai;

-- 1. Centralized Users Table (Shared across all computers)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    age_years INT NOT NULL,
    sex VARCHAR(20) NOT NULL,
    height_cm FLOAT NOT NULL,
    weight_kg FLOAT NOT NULL,
    activity_level VARCHAR(50) NOT NULL,
    goal VARCHAR(50) NOT NULL,
    assessment_json TEXT,
    created_at VARCHAR(50),
    updated_at VARCHAR(50),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Diet Logs Table (History of eaten meals and doctor exports)
CREATE TABLE IF NOT EXISTS diet_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) DEFAULT 'default',
    date VARCHAR(20) NOT NULL,
    timestamp VARCHAR(50) NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    food_name VARCHAR(255) NOT NULL,
    portion_desc VARCHAR(255) DEFAULT '',
    calories FLOAT NOT NULL,
    protein_g FLOAT DEFAULT 0.0,
    carbs_g FLOAT DEFAULT 0.0,
    fat_g FLOAT DEFAULT 0.0,
    is_cheat INT DEFAULT 0,
    notes TEXT,
    INDEX idx_user_date (user_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Planner Items Table (Custom entries and individual food checklists)
CREATE TABLE IF NOT EXISTS planner_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) DEFAULT 'default',
    date VARCHAR(20) NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    food_name VARCHAR(255) NOT NULL,
    portion_desc VARCHAR(255) DEFAULT '',
    weight_g FLOAT DEFAULT 100.0,
    calories FLOAT NOT NULL,
    protein_g FLOAT DEFAULT 0.0,
    carbs_g FLOAT DEFAULT 0.0,
    fat_g FLOAT DEFAULT 0.0,
    is_completed INT DEFAULT 0,
    is_custom INT DEFAULT 1,
    notes TEXT,
    INDEX idx_user_date_plan (user_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
