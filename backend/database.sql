CREATE DATABASE IF NOT EXISTS sportpath_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sportpath_db;

CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    age TINYINT UNSIGNED NULL,
    sport VARCHAR(120) NULL,
    location VARCHAR(160) NULL,
    bio TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admins (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sports (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    slug VARCHAR(140) NOT NULL UNIQUE,
    description TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS athletes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sport_id INT UNSIGNED NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT NULL,
    FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tournaments (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    level VARCHAR(80) NOT NULL,
    sport VARCHAR(120) NULL,
    location VARCHAR(160) NULL,
    event_date DATE NULL,
    description TEXT NULL
);

CREATE TABLE IF NOT EXISTS scholarships (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    provider VARCHAR(160) NULL,
    eligibility TEXT NULL,
    url VARCHAR(500) NULL,
    description TEXT NULL
);

CREATE TABLE IF NOT EXISTS careers (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(180) NOT NULL UNIQUE,
    description TEXT NULL,
    skills TEXT NULL,
    pathway TEXT NULL
);

CREATE TABLE IF NOT EXISTS academies (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    type VARCHAR(80) NULL,
    location VARCHAR(160) NULL,
    sport VARCHAR(120) NULL,
    description TEXT NULL,
    website VARCHAR(500) NULL
);

CREATE TABLE IF NOT EXISTS equipment (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sport VARCHAR(120) NOT NULL,
    name VARCHAR(180) NOT NULL,
    description TEXT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NULL,
    name VARCHAR(120) NULL,
    email VARCHAR(255) NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

INSERT IGNORE INTO sports (name, slug, description) VALUES
('Cricket', 'cricket', 'Batting, bowling, fielding, coaching, and match strategy.'),
('Football', 'football', 'Team play, stamina, tactical awareness, and professional pathways.'),
('Basketball', 'basketball', 'Fast-paced teamwork, fitness, shooting, and defense skills.'),
('Volleyball', 'volleyball', 'Vertical jump, timing, teamwork, and tactical coordination.'),
('Badminton', 'badminton', 'Agility, reflexes, and endurance in an individual racket sport.'),
('Tennis', 'tennis', 'Precision, movement, and mental toughness from a young age.'),
('Table Tennis', 'table-tennis', 'Speed, footwork, and quick decision making.'),
('Kabaddi', 'kabaddi', 'Strength, strategy, and endurance for contact sport training.'),
('Kho Kho', 'kho-kho', 'Tag-based agility, quick turns, and pace management.'),
('Swimming', 'swimming', 'Water endurance, technique, breath control, and race strategy.'),
('Wrestling', 'wrestling', 'Strength, balance, technique, and discipline in combat sports.'),
('Boxing', 'boxing', 'Power, timing, defense, and focus in competitive fighting.'),
('Judo', 'judo', 'Throwing, grappling, and control through skill and balance.'),
('Karate', 'karate', 'Precision, discipline, and striking techniques.'),
('Taekwondo', 'taekwondo', 'Flexibility, speed, and tactical kicking skills.'),
('Archery', 'archery', 'Focus, posture, control, and accuracy under pressure.'),
('Shooting', 'shooting', 'Stability, concentration, and technical discipline.'),
('Gymnastics', 'gymnastics', 'Flexibility, balance, coordination, and rhythm.'),
('Weightlifting', 'weightlifting', 'Explosive strength and barbell technique.'),
('Powerlifting', 'powerlifting', 'Maximum strength across squat, bench, and deadlift.'),
('Bodybuilding', 'bodybuilding', 'Muscle development, symmetry, and physique training.'),
('Cycling', 'cycling', 'Endurance, cadence, and performance across road and track cycling.'),
('Skateboarding', 'skateboarding', 'Balance, creativity, and technical trick progression.'),
('Golf', 'golf', 'Precision, consistency, and strategic course management.'),
('Chess', 'chess', 'Strategy, pattern recognition, and tactical planning.'),
('Rugby', 'rugby', 'Teamwork, tackling, passing, and physical endurance.'),
('Baseball', 'baseball', 'Batting, pitching, fielding, and team coordination.'),
('Softball', 'softball', 'Fast-action field play, timing, and hitting skill.'),
('Handball', 'handball', 'Speed, coordination, and tactical attacking play.'),
('Running', 'running', 'Sprint, middle-distance, and long-distance events.'),
('Sprint', 'sprint', 'Explosive acceleration and race-start technique.'),
('Marathon', 'marathon', 'Endurance, pacing, and long-run training.'),
('Relay', 'relay-race', 'Speed, baton exchange, and team coordination.'),
('High Jump', 'high-jump', 'Explosive power, technique, and timing.'),
('Long Jump', 'long-jump', 'Speed, takeoff mechanics, and landing control.'),
('Triple Jump', 'triple-jump', 'Rhythm, power, and sequencing across phases.'),
('Shot Put', 'shot-put', 'Strength, balance, and rotational technique.'),
('Discus Throw', 'discus-throw', 'Spin mechanics, timing, and body control.'),
('Javelin Throw', 'javelin-throw', 'Coordination, power, and throwing rhythm.');
