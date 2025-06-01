SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables to ensure no conflicts.
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS journeys;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS user_subscriptions;
DROP TABLE IF EXISTS subscription_payments;
DROP TABLE IF EXISTS achievements;
DROP TABLE IF EXISTS user_achievements;
DROP TABLE IF EXISTS achievement_leaderboard;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS event_comments;
DROP TABLE IF EXISTS user_reactions;
DROP TABLE IF EXISTS private_messages;
DROP TABLE IF EXISTS comment_reports;
DROP TABLE IF EXISTS user_follows;
DROP TABLE IF EXISTS departure_board_events;
DROP TABLE IF EXISTS event_images

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    password_hash CHAR(60) BINARY NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    location VARCHAR(50),
    profile_image VARCHAR(255),
    personal_description TEXT,
    role ENUM('traveller', 'editor', 'admin') NOT NULL DEFAULT 'traveller',
    shareable TINYINT NOT NULL DEFAULT 1, -- Indicates whether the user's journeys are shareable (1 = Yes, 0 = No)
    status ENUM('active', 'banned') NOT NULL DEFAULT 'active'
);

CREATE TABLE journeys (
    journey_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('private', 'public') NOT NULL DEFAULT 'private',
    is_hidden TINYINT NOT NULL DEFAULT 0,  -- Indicates whether the journey is hidden (0 = No, 1 = Yes)
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- The timestamp when the item was last updated, automatically updated to current time on each update
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT  -- Ensures user_id references a valid user in the users table, preventing deletion of users with associated records
);

CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    journey_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    location VARCHAR(100),
    event_image VARCHAR(255),
    FOREIGN KEY (journey_id) REFERENCES journeys(journey_id) ON DELETE CASCADE  -- Ensures journey_id references a valid journey in the journeys table, and deletes related records if the referenced journey is deleted
);

CREATE TABLE announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recipient_id INT DEFAULT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    level ENUM('high', 'medium', 'low') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT,  -- Ensures user_id references a valid user in the users table, preventing deletion of users with associated records
    FOREIGN KEY (recipient_id) REFERENCES users(user_id) ON DELETE RESTRICT
);

CREATE TABLE subscriptions (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,                
    duration_months INT NOT NULL,             
    is_free_trial TINYINT NOT NULL DEFAULT 0, 
    discount_percent DECIMAL(5,2), 
    price_nzd_excl_gst DECIMAL(5,2),         
    price_nzd_incl_gst DECIMAL(5,2),         
    is_admin_grantable TINYINT NOT NULL DEFAULT 0
);

CREATE TABLE user_subscriptions (
    user_subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subscription_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('active', 'expired') NOT NULL DEFAULT 'active',
    gifted_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
);

CREATE TABLE subscription_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    billing_country VARCHAR(100) NOT NULL,
    billing_address VARCHAR(100) NOT NULL,
    amount_paid DECIMAL(5,2) NOT NULL,
    gst_amount DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    card_number VARCHAR(19) NOT NULL,
    expiry_date VARCHAR(7) NOT NULL,
    cvv VARCHAR(4) NOT NULL,                    
    user_subscription_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (user_subscription_id) REFERENCES user_subscriptions(user_subscription_id)
);

CREATE TABLE achievements (
  achievement_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(45) NULL,
  icon_url VARCHAR(255) NOT NULL,
  is_premium_only TINYINT NOT NULL DEFAULT 0,
  condition_type ENUM('One-time', 'First-time', 'Cumulative') NOT NULL,
  condition_value INT NULL
);

CREATE TABLE user_achievements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  achievement_id INT NOT NULL,
  is_unlocked TINYINT NOT NULL DEFAULT 0,
  unlocked_at DATETIME NULL,
  progress INT NULL DEFAULT 0,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  create_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `user_id_idx` (`user_id` ASC) VISIBLE,
  INDEX `achievement_id_idx` (`achievement_id` ASC) VISIBLE,
  CONSTRAINT `fk_user_achievement_user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES users (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `achievement_id`
    FOREIGN KEY (`achievement_id`)
    REFERENCES achievements (`achievement_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE achievement_leaderboard (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  total_achievements INT NOT NULL,
  last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `user_id_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_leaderboard_user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES users (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL
);

ALTER TABLE events 
ADD COLUMN location_id INT,
ADD COLUMN departure_location_id INT,
ADD COLUMN destination_location_id INT,
ADD FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE RESTRICT,
ADD FOREIGN KEY (departure_location_id) REFERENCES locations(location_id) ON DELETE RESTRICT,
ADD FOREIGN KEY (destination_location_id) REFERENCES locations(location_id) ON DELETE RESTRICT;

CREATE TABLE event_comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_hidden TINYINT NOT NULL DEFAULT 0,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE user_reactions (
    reaction_id INT AUTO_INCREMENT PRIMARY KEY,
    target_type ENUM('comment', 'event') NOT NULL,
    target_id INT NOT NULL,
    user_id INT NOT NULL,
    reaction_type ENUM('like', 'dislike') NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(target_type, target_id, user_id), -- A user can only like or dislike the same comment once.
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE private_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    sent_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE comment_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT NOT NULL,
    reported_by INT NOT NULL,
    reason ENUM('abusive', 'offensive', 'spam') NOT NULL,
    report_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INT,
    review_action ENUM('keep', 'hidden', 'escalated'),
    reviewed_at DATETIME,
    FOREIGN KEY (comment_id) REFERENCES event_comments(comment_id) ON DELETE CASCADE,
    FOREIGN KEY (reported_by) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(user_id)
);

CREATE TABLE user_follows (
    user_follow_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    followed_id INT NOT NULL,  -- The followed ID (which could be a journey, user, or location)
    follow_type ENUM('journey', 'user', 'location') NOT NULL,
    followed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    -- Use a composite unique key to ensure that each user has only one follow record for each object (journey, user, or location).
    UNIQUE(user_id, followed_id, follow_type)  
);

CREATE TABLE departure_board_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    user_follow_id INT NOT NULL,
    FOREIGN KEY (user_follow_id) REFERENCES user_follows(user_follow_id) ON DELETE CASCADE
);

CREATE TABLE event_reactions (
    reaction_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    reaction_type ENUM('like', 'love', 'wow') NOT NULL DEFAULT 'like',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

ALTER TABLE users MODIFY role ENUM('traveller', 'editor', 'admin', 'moderator') NOT NULL DEFAULT 'traveller';

ALTER TABLE users 
    ADD COLUMN subscription_end_date DATE,
    ADD COLUMN remaining_months INT UNSIGNED NOT NULL DEFAULT 0,
    ADD COLUMN subscription_status ENUM('Free', 'Trial', 'Premium') NOT NULL DEFAULT 'Free',
    ADD COLUMN is_public_profile TINYINT NOT NULL DEFAULT 0,
    ADD COLUMN is_trial_used TINYINT NOT NULL DEFAULT 0;

ALTER TABLE journeys
MODIFY status ENUM('private', 'public', 'published') NOT NULL DEFAULT 'private';

ALTER TABLE journeys
ADD COLUMN cover_image VARCHAR(255);

-- 22/05/2025 add
ALTER TABLE private_messages
ADD COLUMN is_read TINYINT NOT NULL DEFAULT 0,
ADD INDEX idx_receiver_read (receiver_id, is_read),
ADD INDEX idx_conversation (sender_id, receiver_id);

-- 26/05/2025 add
ALTER TABLE user_achievements
ADD UNIQUE KEY unique_user_achievement (user_id, achievement_id);

ALTER TABLE announcements
    ADD COLUMN is_read TINYINT NOT NULL DEFAULT 0;
ALTER TABLE announcements
    ADD COLUMN subscription_end_date DATE DEFAULT NULL;
ALTER TABLE announcements MODIFY COLUMN user_id INT NULL;

SET FOREIGN_KEY_CHECKS = 1;

-- 31/05/2025 add
CREATE TABLE event_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);
