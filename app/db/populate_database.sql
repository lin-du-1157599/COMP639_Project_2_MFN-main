-- Sample data for New Zealand local trips travel journal application
-- Using the same password hash for all users: '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW' (Admin1pass*)

-- Users: 2 admins, 5 editors, 20 travelers
INSERT INTO users (username, password_hash, email, first_name, last_name, location, profile_image, personal_description, role, shareable, status) VALUES
-- Admins (2)
('admin1', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'admin1@example.com', 'Sarah', 'Johnson', 'Wellington', 'profiles/alina.jpg', 'Main administrator of the travel journal site. Avid traveler and photographer.', 'admin', 1, 'active'),
('admin2', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'admin2@example.com', 'David', 'Chen', 'Auckland', 'profiles/admin2.jpg', 'System administrator and hiking enthusiast. Loves exploring NZ\'s national parks.', 'admin', 1, 'active'),

-- Editors (5)
('editor1', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'editor1@example.com', 'Emma', 'Williams', 'Christchurch', 'profiles/editor1.jpg', 'Content editor and travel blogger specializing in South Island adventures.', 'editor', 1, 'active'),
('editor2', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'editor2@example.com', 'James', 'Smith', 'Dunedin', 'profiles/editor2.jpg', 'Professional editor with a passion for cultural tourism and local cuisines.', 'editor', 1, 'active'),
('editor3', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'editor3@example.com', 'Olivia', 'Brown', 'Hamilton', 'profiles/editor3.jpg', 'Editor with expertise in North Island travels and Māori cultural sites.', 'editor', 1, 'active'),
('editor4', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'editor4@example.com', 'Daniel', 'Taylor', 'Tauranga', 'profiles/editor4.jpg', 'Former tour guide turned editor. Expert on coastal NZ destinations.', 'editor', 1, 'active'),
('editor5', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'editor5@example.com', 'Sophie', 'Wilson', 'Nelson', 'profiles/editor5.jpg', 'Nature photographer and editor specializing in nature and wildlife journeys.', 'editor', 1, 'active'),

-- Travelers (20)
('traveler1', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler1@example.com', 'Michael', 'Johnson', 'Wellington', 'profiles/traveler1.jpg', 'Adventure seeker and outdoor enthusiast. Loves hiking and kayaking around NZ.', 'traveller', 1, 'active'),
('traveler2', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler2@example.com', 'Jessica', 'Lee', 'Auckland', NULL, 'Foodie traveler exploring New Zealand\'s culinary scenes.', 'traveller', 1, 'active'),
('traveler3', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler3@example.com', 'Ryan', 'Miller', 'Queenstown', NULL, 'Extreme sports enthusiast. Always looking for the next adrenaline rush.', 'traveller', 1, 'active'),
('traveler4', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler4@example.com', 'Emily', 'Clark', 'Rotorua', NULL, 'Backpacker exploring New Zealand on a budget. Loves hostels and meeting locals.', 'traveller', 1, 'active'),
('traveler5', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler5@example.com', 'Joshua', 'Walker', 'Napier', NULL, 'Wine enthusiast visiting all of New Zealand\'s vineyards.', 'traveller', 1, 'active'),
('traveler6', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler6@example.com', 'Hannah', 'Anderson', 'Whangarei', NULL, 'Nature photographer capturing New Zealand\'s stunning landscapes.', 'traveller', 1, 'active'),
('traveler7', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler7@example.com', 'Matthew', 'Thompson', 'Gisborne', NULL, 'Surfing enthusiast chasing the best waves around New Zealand.', 'traveller', 1, 'active'),
('traveler8', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler8@example.com', 'Sophia', 'Martinez', 'Invercargill', NULL, 'Southern explorer discovering the hidden gems of South Island.', 'traveller', 1, 'active'),
('traveler9', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler9@example.com', 'Andrew', 'Robinson', 'New Plymouth', NULL, 'Mountain biker exploring New Zealand\'s best trails.', 'traveller', 1, 'active'),
('traveler10', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler10@example.com', 'Mia', 'Harris', 'Taupo', NULL, 'Hot springs enthusiast and amateur geologist.', 'traveller', 1, 'active'),
('traveler11', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler11@example.com', 'Ethan', 'Lewis', 'Wanaka', NULL, 'Winter sports fan covering all of New Zealand\'s ski fields.', 'traveller', 1, 'active'),
('traveler12', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler12@example.com', 'Charlotte', 'Turner', 'Blenheim', NULL, 'Wine tour guide sharing the best of NZ\'s wine regions.', 'traveller', 1, 'active'),
('traveler13', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler13@example.com', 'Daniel', 'Parker', 'Timaru', NULL, 'Motorcycle enthusiast touring New Zealand on two wheels.', 'traveller', 0, 'active'), -- Can't share
('traveler14', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler14@example.com', 'Amelia', 'Collins', 'Palmerston North', NULL, 'Bird watcher documenting New Zealand\'s unique avian species.', 'traveller', 0, 'active'), -- Can't share
('traveler15', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler15@example.com', 'Benjamin', 'Edwards', 'Whanganui', NULL, 'River enthusiast exploring New Zealand\'s waterways by canoe.', 'traveller', 1, 'banned'), -- Banned user
('traveler16', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler16@example.com', 'Isabella', 'Wright', 'Oamaru', NULL, 'Historic architecture fan and penguin observer.', 'traveller', 1, 'active'),
('traveler17', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler17@example.com', 'William', 'Young', 'Cambridge', NULL, 'Cycling enthusiast touring New Zealand\'s scenic routes.', 'traveller', 1, 'active'),
('traveler18', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler18@example.com', 'Grace', 'Scott', 'Kaikoura', NULL, 'Marine wildlife photographer focusing on whales and dolphins.', 'traveller', 1, 'active'),
('traveler19', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler19@example.com', 'Alexander', 'Green', 'Te Anau', NULL, 'Fiordland explorer and landscape photographer.', 'traveller', 1, 'active'),
('traveler20', '$2b$12$sLDeXJhQn2L/FNv8qGkDL.Cw8BDaszP2/oIPYr2Fmx2kG237Qa3hW', 'traveler20@example.com', 'Zoe', 'Mitchell', 'Lincoln', NULL, 'COMP639 student documenting travels through Canterbury.', 'traveller', 1, 'active');

-- Journeys: 20 total, 10 public/10 private
-- Note: Some users have multiple journeys, some have one, some have none
INSERT INTO journeys (user_id, title, description, status, is_hidden, start_date) VALUES
-- Admin journeys
(1, 'Wellington to Marlborough', 'A scenic journey from Wellington to Marlborough wine region via ferry.', 'public', 0, '2024-12-15 08:00:00'),
(2, 'Auckland to Rotorua Road Trip', 'Exploring geothermal wonders on a weekend road trip from Auckland to Rotorua.', 'public', 0, '2024-11-20 09:00:00'),

-- Editor journeys
(3, 'Christchurch to Akaroa Day Trip', 'A beautiful day trip from Christchurch to the French-inspired harbor town of Akaroa.', 'public', 0, '2025-01-05 08:30:00'),
(4, 'Dunedin Street Art Tour', 'Exploring the vibrant street art scene in Dunedin\'s cultural district.', 'private', 0, '2024-10-25 10:00:00'),
(5, 'Hamilton Gardens Experience', 'A peaceful day exploring the internationally acclaimed Hamilton Gardens.', 'public', 0, '2025-02-14 09:00:00'),

-- Traveler journeys (multiple journeys for some users)
(8, 'Queenstown Winter Adventure', 'A week of skiing, snowboarding, and adventure sports in Queenstown.', 'public', 0, '2024-07-10 07:00:00'),
(8, 'Milford Sound Expedition', 'Exploring the breathtaking fjords of Milford Sound.', 'private', 0, '2024-09-05 06:30:00'),
(9, 'Rotorua Geothermal Tour', 'Exploring the geothermal wonders and Māori culture in Rotorua.', 'public', 0, '2025-01-20 09:00:00'),
(10, 'Hawke\'s Bay Wine Tour', 'A weekend sampling the finest wines from Hawke\'s Bay region.', 'public', 0, '2024-11-15 11:00:00'),
(11, 'Bay of Islands Sailing Trip', 'A three-day sailing adventure around the beautiful Bay of Islands.', 'private', 0, '2024-12-28 08:00:00'),
(12, 'West Coast Wilderness Trail', 'Cycling the spectacular West Coast Wilderness Trail on the South Island.', 'private', 0, '2025-02-05 07:30:00'),
(13, 'Tongariro Alpine Crossing', 'Hiking the famous Tongariro Alpine Crossing, one of NZ\'s best day walks.', 'public', 0, '2024-10-18 06:00:00'),
(14, 'Coromandel Peninsula Road Trip', 'Exploring beaches, hot springs, and forests of the Coromandel Peninsula.', 'private', 0, '2025-01-08 09:30:00'),
(15, 'Abel Tasman Coastal Track', 'Five days hiking the beautiful Abel Tasman Coastal Track.', 'public', 1, '2024-11-30 07:00:00'), -- Hidden journey from banned user
(17, 'Waitomo Caves Adventure', 'Exploring the glowworm caves and black water rafting in Waitomo.', 'public', 0, '2024-12-10 10:00:00'),
(19, 'Kaikoura Whale Watching', 'Marine wildlife encounters in the coastal town of Kaikoura.', 'private', 0, '2025-02-20 07:30:00'),
(20, 'Fiordland National Park Trek', 'Hiking through the majestic landscapes of Fiordland National Park.', 'public', 0, '2024-11-05 06:30:00'),
(20, 'COMP639 Workshop Trip to Lincoln', 'My journey to Lincoln for the COMP639 Studio Project Workshop.', 'private', 0, '2025-03-15 08:00:00'),
(21, 'Aoraki/Mount Cook Exploration', 'Exploring New Zealand\'s highest mountain and surrounding alpine environment.', 'private', 0, '2025-01-25 08:30:00'),
(26, 'Stewart Island Wildlife Weekend', 'Bird watching and wildlife spotting on New Zealand\'s third largest island.', 'public', 0, '2024-12-05 09:00:00');

-- Events: 5-10 events per journey, with photos for some events
INSERT INTO events (journey_id, title, description, start_time, end_time, location, event_image) VALUES
-- Journey 1: Wellington to Marlborough (5 events)
(1, 'Wellington City Exploration', 'Morning walk around Wellington city center before the ferry.', '2024-12-15 08:30:00', '2024-12-15 10:30:00', 'Wellington CBD', 'events/wellington_cbd.jpg'),
(1, 'Ferry Crossing Cook Strait', 'Scenic ferry crossing from Wellington to Picton with amazing views.', '2024-12-15 11:00:00', '2024-12-15 14:30:00', 'Cook Strait Ferry', 'events/cook_strait_ferry.jpg'),
(1, 'Picton Harbor Lunch', 'Fresh seafood lunch at a waterfront restaurant in Picton.', '2024-12-15 15:00:00', '2024-12-15 16:30:00', 'Picton Harbor', NULL),
(1, 'Wine Tasting at Cloudy Bay', 'Sampling premium wines at the famous Cloudy Bay Vineyard.', '2024-12-15 17:00:00', '2024-12-15 18:30:00', 'Cloudy Bay Vineyard, Marlborough', 'events/cloudy_bay.jpg'),
(1, 'Dinner at Local Restaurant', 'Farm-to-table dinner featuring local Marlborough produce.', '2024-12-15 19:30:00', '2024-12-15 21:30:00', 'Arbour Restaurant, Marlborough', NULL),

-- Journey 2: Auckland to Rotorua Road Trip (6 events)
(2, 'Departure from Auckland', 'Left Auckland early morning to beat the traffic.', '2024-11-20 09:00:00', '2024-11-20 10:30:00', 'Auckland City', NULL),
(2, 'Coffee Stop in Hamilton', 'Quick coffee break and stretch in Hamilton Gardens.', '2024-11-20 11:30:00', '2024-11-20 12:30:00', 'Hamilton Gardens', 'events/hamilton_gardens.jpg'),
(2, 'Lunch at Tirau', 'Lunch stop at the quirky town of Tirau with its corrugated iron art.', '2024-11-20 13:30:00', '2024-11-20 14:30:00', 'Tirau', 'events/tirau.jpg'),
(2, 'Arrival at Rotorua', 'Checked into accommodation and first encounter with the distinctive sulfur smell!', '2024-11-20 16:00:00', '2024-11-20 17:00:00', 'Rotorua', NULL),
(2, 'Visit to Te Puia', 'Evening visit to Te Puia to see Pōhutu geyser and Māori cultural performance.', '2024-11-20 18:00:00', '2024-11-20 21:00:00', 'Te Puia, Rotorua', 'events/te_puia.jpg'),
(2, 'Polynesian Spa Relaxation', 'Late night relaxation in the mineral hot pools at Polynesian Spa.', '2024-11-20 21:30:00', '2024-11-20 23:00:00', 'Polynesian Spa, Rotorua', NULL),

-- Journey 3: Christchurch to Akaroa Day Trip (5 events)
(3, 'Departure from Christchurch', 'Early morning start from Christchurch city center.', '2025-01-05 08:30:00', '2025-01-05 09:30:00', 'Christchurch', NULL),
(3, 'Scenic Drive over Banks Peninsula', 'Stunning drive over the volcanic Banks Peninsula with panoramic views.', '2025-01-05 09:30:00', '2025-01-05 11:00:00', 'Banks Peninsula', 'events/banks_peninsula.jpg'),
(3, 'Arrival in Akaroa', 'First impressions of the charming French-inspired harbor town.', '2025-01-05 11:00:00', '2025-01-05 11:30:00', 'Akaroa', 'events/akaroa_harbor.jpg'),
(3, 'Dolphin Watching Cruise', 'Boat tour to see the rare Hector\'s dolphins in Akaroa Harbor.', '2025-01-05 12:00:00', '2025-01-05 14:30:00', 'Akaroa Harbor', 'events/hectors_dolphins.jpg'),
(3, 'French-Inspired Dinner', 'Delicious dinner at a local French restaurant before returning to Christchurch.', '2025-01-05 17:30:00', '2025-01-05 19:00:00', 'The Little Bistro, Akaroa', NULL),

-- Journey 4: Dunedin Street Art Tour (5 events)
(4, 'Coffee at The Perc', 'Starting the day with excellent coffee at a local favorite café.', '2024-10-25 10:00:00', '2024-10-25 11:00:00', 'The Perc, Dunedin', NULL),
(4, 'Stuart Street Murals', 'Exploring the large-scale murals on Stuart Street buildings.', '2024-10-25 11:30:00', '2024-10-25 12:30:00', 'Stuart Street, Dunedin', 'events/stuart_street_art.jpg'),
(4, 'Lunch at Vogel Street', 'Quick lunch at a hip café in the revitalized warehouse precinct.', '2024-10-25 13:00:00', '2024-10-25 14:00:00', 'Vogel Street Kitchen, Dunedin', NULL),
(4, 'Warehouse Precinct Street Art', 'Exploring the street art in Dunedin\'s trendy warehouse district.', '2024-10-25 14:00:00', '2024-10-25 16:00:00', 'Warehouse Precinct, Dunedin', 'events/warehouse_art.jpg'),
(4, 'Street Art Alleyways', 'Discovering hidden artwork in small alleyways around the city.', '2024-10-25 16:30:00', '2024-10-25 18:00:00', 'Central Dunedin', NULL),

-- Journey 5: Hamilton Gardens Experience (5 events)
(5, 'Arrival at Hamilton Gardens', 'Beginning our exploration of the internationally acclaimed gardens.', '2025-02-14 09:00:00', '2025-02-14 09:30:00', 'Hamilton Gardens', 'events/hamilton_gardens_entrance.jpg'),
(5, 'Italian Renaissance Garden', 'Exploring the perfectly symmetrical Italian Renaissance Garden.', '2025-02-14 09:30:00', '2025-02-14 10:30:00', 'Italian Renaissance Garden, Hamilton Gardens', NULL),
(5, 'Japanese Garden of Contemplation', 'Peaceful moments in the Japanese Garden of Contemplation.', '2025-02-14 10:45:00', '2025-02-14 11:45:00', 'Japanese Garden, Hamilton Gardens', 'events/japanese_garden.jpg'),
(5, 'Lunch at Gardens Café', 'Relaxing lunch overlooking the beautiful gardens.', '2025-02-14 12:00:00', '2025-02-14 13:30:00', 'Hamilton Gardens Café', NULL),
(5, 'Sustainable Backyard Garden', 'Learning about sustainable gardening practices in the practical garden section.', '2025-02-14 13:45:00', '2025-02-14 15:00:00', 'Sustainable Backyard Garden, Hamilton Gardens', NULL),

-- Journey 6: Queenstown Winter Adventure (8 events)
(6, 'Arrival in Queenstown', 'Landing at Queenstown Airport with stunning mountain views.', '2024-07-10 07:00:00', '2024-07-10 08:30:00', 'Queenstown Airport', 'events/queenstown_arrival.jpg'),
(6, 'Check-in at Accommodation', 'Settling into our cozy chalet near the center of town.', '2024-07-10 09:30:00', '2024-07-10 10:30:00', 'Queenstown Central', NULL),
(6, 'First Day Skiing at Coronet Peak', 'Perfect conditions for our first day on the slopes!', '2024-07-11 08:00:00', '2024-07-11 16:00:00', 'Coronet Peak Ski Field', 'events/coronet_peak.jpg'),
(6, 'Fergburger Dinner', 'Famous burgers at the legendary Fergburger after a day on the slopes.', '2024-07-11 18:00:00', '2024-07-11 19:30:00', 'Fergburger, Queenstown', NULL),
(6, 'The Remarkables Ski Day', 'Challenging runs at The Remarkables ski field with incredible views.', '2024-07-12 08:30:00', '2024-07-12 16:30:00', 'The Remarkables Ski Field', 'events/remarkables.jpg'),
(6, 'Onsen Hot Pools', 'Relaxing soak in the Onsen Hot Pools overlooking the Shotover River canyon.', '2024-07-12 18:00:00', '2024-07-12 19:30:00', 'Onsen Hot Pools, Queenstown', NULL),
(6, 'Shotover Jet Boat Ride', 'Thrilling jet boat ride through the narrow Shotover River canyons.', '2024-07-13 10:00:00', '2024-07-13 11:30:00', 'Shotover River, Queenstown', 'events/shotover_jet.jpg'),
(6, 'Skyline Gondola & Luge', 'Riding the gondola up Bob\'s Peak for amazing views and luge rides.', '2024-07-13 14:00:00', '2024-07-13 17:00:00', 'Skyline Queenstown', NULL),

-- Journey 7: Milford Sound Expedition (6 events)
(7, 'Departure from Queenstown', 'Early morning bus departure for Milford Sound.', '2024-09-05 06:30:00', '2024-09-05 07:00:00', 'Queenstown', NULL),
(7, 'Te Anau Stop', 'Brief stop in Te Anau, the gateway to Fiordland National Park.', '2024-09-05 09:00:00', '2024-09-05 09:30:00', 'Te Anau', 'events/te_anau.jpg'),
(7, 'Mirror Lakes', 'Photo stop at the famously reflective Mirror Lakes.', '2024-09-05 10:30:00', '2024-09-05 11:00:00', 'Mirror Lakes, Fiordland', 'events/mirror_lakes.jpg'),
(7, 'Homer Tunnel', 'Passing through the impressive Homer Tunnel carved through solid rock.', '2024-09-05 12:00:00', '2024-09-05 12:30:00', 'Homer Tunnel, Milford Road', NULL),
(7, 'Milford Sound Cruise', 'Scenic cruise along Milford Sound, seeing waterfalls and wildlife.', '2024-09-05 13:30:00', '2024-09-05 15:30:00', 'Milford Sound', 'events/milford_sound.jpg'),
(7, 'Return Journey to Queenstown', 'Long but scenic drive back to Queenstown.', '2024-09-05 16:00:00', '2024-09-05 20:00:00', 'Milford Road', NULL),

-- Journey 8: Rotorua Geothermal Tour (7 events)
(8, 'Check-in at Thermal Resort', 'Arriving at our accommodation with natural hot pools.', '2025-01-20 09:00:00', '2025-01-20 10:00:00', 'Rotorua', NULL),
(8, 'Wai-O-Tapu Thermal Wonderland', 'Exploring the colorful geothermal park including the famous Champagne Pool.', '2025-01-20 11:00:00', '2025-01-20 14:00:00', 'Wai-O-Tapu Thermal Wonderland', 'events/waiotapu.jpg'),
(8, 'Lady Knox Geyser Eruption', 'Watching the daily eruption of the Lady Knox Geyser.', '2025-01-20 10:15:00', '2025-01-20 10:45:00', 'Lady Knox Geyser, Wai-O-Tapu', NULL),
(8, 'Lunch at Rotorua Lakefront', 'Relaxing lunch overlooking Lake Rotorua.', '2025-01-20 14:30:00', '2025-01-20 15:30:00', 'Rotorua Lakefront', NULL),
(8, 'Te Puia Cultural Experience', 'Māori cultural performance and traditional hangi dinner.', '2025-01-20 17:00:00', '2025-01-20 20:00:00', 'Te Puia, Rotorua', 'events/maori_performance.jpg'),
(8, 'Redwoods Treewalk', 'Evening walk on suspended bridges through illuminated Redwood forest.', '2025-01-20 21:00:00', '2025-01-20 22:30:00', 'Redwoods Treewalk, Rotorua', 'events/redwoods_night.jpg'),
(8, 'Hells Gate Mud Bath', 'Therapeutic mud bath and sulfur spa experience.', '2025-01-21 10:00:00', '2025-01-21 12:00:00', 'Hells Gate, Rotorua', NULL),

-- Journey 9: Hawke's Bay Wine Tour (6 events)
(9, 'Arrival in Napier', 'Checking into our Art Deco hotel in the heart of Napier.', '2024-11-15 11:00:00', '2024-11-15 12:00:00', 'Napier', NULL),
(9, 'Art Deco Walking Tour', 'Guided tour of Napier\'s famous Art Deco architecture.', '2024-11-15 13:00:00', '2024-11-15 14:30:00', 'Napier Art Deco District', 'events/napier_art_deco.jpg'),
(9, 'Mission Estate Winery', 'Wine tasting at New Zealand\'s oldest winery.', '2024-11-15 15:00:00', '2024-11-15 16:30:00', 'Mission Estate Winery, Napier', 'events/mission_estate.jpg'),
(9, 'Craggy Range Vineyard', 'Premium wine tasting with spectacular views of Te Mata Peak.', '2024-11-16 10:00:00', '2024-11-16 11:30:00', 'Craggy Range Vineyard, Havelock North', NULL),
(9, 'Lunch at Black Barn Bistro', 'Gourmet lunch at a beautiful vineyard restaurant.', '2024-11-16 12:00:00', '2024-11-16 14:00:00', 'Black Barn Bistro, Havelock North', 'events/black_barn.jpg'),
(9, 'Te Mata Peak Sunset', 'Hiking to the top of Te Mata Peak for sunset views over Hawke\'s Bay.', '2024-11-16 18:00:00', '2024-11-16 20:00:00', 'Te Mata Peak', 'events/te_mata_peak.jpg'),

-- Journey 10: Bay of Islands Sailing Trip (5 events)
(10, 'Arrival in Paihia', 'Checking into waterfront accommodation in Paihia.', '2024-12-28 08:00:00', '2024-12-28 09:30:00', 'Paihia', NULL),
(10, 'Charter Sailboat Departure', 'Setting sail from Paihia wharf on our chartered yacht.', '2024-12-28 10:00:00', '2024-12-28 11:00:00', 'Paihia Wharf', 'events/bay_islands_sailing.jpg'),
(10, 'Roberton Island Snorkeling', 'Anchoring at Roberton Island for swimming and snorkeling.', '2024-12-28 12:00:00', '2024-12-28 14:00:00', 'Roberton Island, Bay of Islands', NULL),
(10, 'Overnight Anchorage', 'Beautiful evening anchored in a sheltered cove.', '2024-12-28 17:00:00', '2024-12-29 08:00:00', 'Assassination Cove, Bay of Islands', 'events/bay_islands_sunset.jpg'),
(10, 'Dolphin Encounter', 'Amazing encounter with a pod of dolphins while sailing.', '2024-12-29 10:00:00', '2024-12-29 11:00:00', 'Bay of Islands', 'events/dolphins.jpg'),

-- Journey 11: West Coast Wilderness Trail (8 events)
(11, 'Arrival in Greymouth', 'Starting point of our cycling adventure.', '2025-02-05 07:30:00', '2025-02-05 08:30:00', 'Greymouth', NULL),
(11, 'Bike Rental and Preparations', 'Getting our bikes and gear ready for the journey.', '2025-02-05 08:30:00', '2025-02-05 09:30:00', 'Greymouth Cycle Hire', NULL),
(11, 'Greymouth to Kumara Ride', 'First leg of the trail through old railway lines and wetlands.', '2025-02-05 09:30:00', '2025-02-05 12:30:00', 'Greymouth to Kumara', 'events/wilderness_trail_1.jpg'),
(11, 'Theatre Royal Hotel Stay', 'Overnight at the historic Theatre Royal Hotel in Kumara.', '2025-02-05 17:00:00', '2025-02-06 08:00:00', 'Theatre Royal Hotel, Kumara', NULL),
(11, 'Kumara to Cowboy Paradise', 'Challenging ride through native forest to Cowboy Paradise.', '2025-02-06 08:30:00', '2025-02-06 13:00:00', 'Kumara to Cowboy Paradise', 'events/cowboy_paradise.jpg'),
(11, 'Cowboy Paradise to Hokitika', 'Scenic downhill ride to Hokitika town.', '2025-02-07 08:00:00', '2025-02-07 12:00:00', 'Cowboy Paradise to Hokitika', NULL),
(11, 'Hokitika Gorge Visit', 'Side trip to see the stunning turquoise waters of Hokitika Gorge.', '2025-02-07 14:00:00', '2025-02-07 16:00:00', 'Hokitika Gorge', 'events/hokitika_gorge.jpg'),
(11, 'Hokitika to Ross', 'Final leg of the trail to the historic gold mining town of Ross.', '2025-02-08 09:00:00', '2025-02-08 12:00:00', 'Hokitika to Ross', NULL),

-- Journey 12: Tongariro Alpine Crossing (5 events)
(12, 'Arrival at National Park Village', 'Checking into lodge accommodation before the big hike.', '2024-10-18 06:00:00', '2024-10-18 07:00:00', 'National Park Village', NULL),
(12, 'Shuttle to Mangatepopo', 'Early morning shuttle to the starting point of the crossing.', '2024-10-18 07:30:00', '2024-10-18 08:00:00', 'Mangatepopo Car Park', NULL),
(12, 'Climb to South Crater', 'Steep climb from Mangatepopo Valley to South Crater.', '2024-10-18 08:30:00', '2024-10-18 10:30:00', 'South Crater, Tongariro', 'events/south_crater.jpg'),
(12, 'Red Crater and Emerald Lakes', 'The highest point of the crossing with views of the stunning Emerald Lakes.', '2024-10-18 11:00:00', '2024-10-18 12:30:00', 'Emerald Lakes, Tongariro', 'events/emerald_lakes.jpg'),
(12, 'Descent to Ketetahi', 'Long descent with views of Lake Taupo in the distance.', '2024-10-18 13:00:00', '2024-10-18 15:30:00', 'Ketetahi Car Park', NULL),

-- Journey 13: Coromandel Peninsula Road Trip (7 events)
(13, 'Departure from Auckland', 'Setting off from Auckland towards the Coromandel Peninsula.', '2025-01-08 09:30:00', '2025-01-08 11:30:00', 'Auckland to Thames', NULL),
(13, 'Thames Historic Walk', 'Exploring the gold mining history of Thames.', '2025-01-08 12:00:00', '2025-01-08 13:30:00', 'Thames', NULL),
(13, 'Driving the 309 Road', 'Taking the scenic 309 Road through native forest to Coromandel Town.', '2025-01-08 14:00:00', '2025-01-08 15:30:00', '309 Road, Coromandel', 'events/309_road.jpg'),
(13, 'Driving Creek Railway', 'Riding the narrow-gauge mountain railway with amazing views.', '2025-01-08 16:00:00', '2025-01-08 17:30:00', 'Driving Creek Railway, Coromandel Town', 'events/driving_creek.jpg'),
(13, 'Hot Water Beach Dig', 'Digging our own hot pool at Hot Water Beach at low tide.', '2025-01-09 05:30:00', '2025-01-09 07:30:00', 'Hot Water Beach', 'events/hot_water_beach.jpg'),
(13, 'Cathedral Cove Hike', 'Walking to the famous natural archway at Cathedral Cove.', '2025-01-09 09:00:00', '2025-01-09 12:00:00', 'Cathedral Cove', 'events/cathedral_cove.jpg'),
(13, 'New Chums Beach', 'Visit to the pristine and secluded New Chums Beach.', '2025-01-09 14:00:00', '2025-01-09 17:00:00', 'New Chums Beach, Coromandel', NULL),

-- Journey 14: Abel Tasman Coastal Track (Hidden journey from banned user, 6 events)
(14, 'Arrival in Marahau', 'Starting point for the Abel Tasman Coastal Track.', '2024-11-30 07:00:00', '2024-11-30 08:00:00', 'Marahau', NULL),
(14, 'Marahau to Anchorage', 'First day\'s hike along golden beaches and through native forest.', '2024-11-30 08:30:00', '2024-11-30 14:00:00', 'Abel Tasman Coastal Track', 'events/abel_tasman_track.jpg'),
(14, 'Anchorage Bay Camping', 'Setting up camp at the beautiful Anchorage Bay.', '2024-11-30 14:30:00', '2024-11-30 16:00:00', 'Anchorage Bay, Abel Tasman', NULL),
(14, 'Cleopatra\'s Pool Visit', 'Side trip to the natural rock pools with water slide.', '2024-11-30 16:30:00', '2024-11-30 18:00:00', 'Cleopatra\'s Pool, Abel Tasman', 'events/cleopatras_pool.jpg'),
(14, 'Anchorage to Bark Bay', 'Second day\'s hike crossing the famous Falls River swing bridge.', '2024-12-01 08:00:00', '2024-12-01 13:00:00', 'Abel Tasman Coastal Track', NULL),
(14, 'Water Taxi Return', 'Scenic water taxi ride back to Marahau, viewing seal colonies.', '2024-12-03 14:00:00', '2024-12-03 15:30:00', 'Abel Tasman Coast', 'events/abel_tasman_water_taxi.jpg'),

-- Journey 15: Waitomo Caves Adventure (5 events)
(15, 'Arrival in Waitomo', 'Checking into accommodation in the small Waitomo village.', '2024-12-10 10:00:00', '2024-12-10 11:00:00', 'Waitomo Village', NULL),
(15, 'Waitomo Glowworm Caves Tour', 'Guided tour of the famous glowworm caves with boat ride.', '2024-12-10 11:30:00', '2024-12-10 13:00:00', 'Waitomo Glowworm Caves', 'events/glowworm_caves.jpg'),
(15, 'Ruakuri Cave Walk', 'Walking tour of Ruakuri Cave with its spectacular limestone formations.', '2024-12-10 14:30:00', '2024-12-10 16:00:00', 'Ruakuri Cave, Waitomo', NULL),
(15, 'Black Water Rafting', 'Tubing through underground rivers in the darkness, lit only by glowworms.', '2024-12-11 09:00:00', '2024-12-11 13:00:00', 'Ruakuri Cave System, Waitomo', 'events/black_water_rafting.jpg'),
(15, 'Marokopa Falls Visit', 'Short drive to see the impressive 35-meter Marokopa Falls.', '2024-12-11 14:30:00', '2024-12-11 16:00:00', 'Marokopa Falls', NULL),

-- Journey 16: Kaikoura Whale Watching (7 events)
(16, 'Drive from Christchurch to Kaikoura', 'Scenic coastal drive north from Christchurch.', '2025-02-20 07:30:00', '2025-02-20 10:00:00', 'Christchurch to Kaikoura', NULL),
(16, 'Check-in at Kaikoura Accommodation', 'Settling into our beachfront accommodation.', '2025-02-20 10:30:00', '2025-02-20 11:30:00', 'Kaikoura', NULL),
(16, 'Lunch at Kaikoura Seafood BBQ', 'Fresh crayfish lunch at the famous roadside seafood BBQ.', '2025-02-20 12:00:00', '2025-02-20 13:30:00', 'Kaikoura Seafood BBQ', 'events/kaikoura_crayfish.jpg'),
(16, 'Whale Watching Tour', 'Boat tour to see giant sperm whales in their natural habitat.', '2025-02-20 14:30:00', '2025-02-20 17:30:00', 'Kaikoura Coast', 'events/whale_watching.jpg'),
(16, 'Peninsula Walkway Sunset', 'Evening walk along the Kaikoura Peninsula Walkway.', '2025-02-20 19:00:00', '2025-02-20 20:30:00', 'Kaikoura Peninsula', 'events/kaikoura_peninsula.jpg'),
(16, 'Dolphin Encounter Swim', 'Swimming with pods of wild dusky dolphins.', '2025-02-21 08:00:00', '2025-02-21 11:00:00', 'Kaikoura Coast', NULL),
(16, 'Seal Colony Visit', 'Visiting the fur seal colony at Ohau Point.', '2025-02-21 12:30:00', '2025-02-21 14:00:00', 'Ohau Point, Kaikoura', 'events/kaikoura_seals.jpg'),

-- Journey 17: Fiordland National Park Trek (8 events)
(17, 'Arrival in Te Anau', 'Gateway town to Fiordland National Park.', '2024-11-05 06:30:00', '2024-11-05 08:00:00', 'Te Anau', NULL),
(17, 'Te Anau Bird Sanctuary', 'Visit to see rare native birds including takahē.', '2024-11-05 09:00:00', '2024-11-05 10:30:00', 'Te Anau Bird Sanctuary', 'events/takahe.jpg'),
(17, 'Lake Te Anau Cruise', 'Afternoon cruise on New Zealand\'s second-largest lake.', '2024-11-05 13:00:00', '2024-11-05 15:00:00', 'Lake Te Anau', NULL),
(17, 'Kepler Track Day Hike', 'Day hike on part of the famous Kepler Track.', '2024-11-06 08:00:00', '2024-11-06 16:00:00', 'Kepler Track, Fiordland', 'events/kepler_track.jpg'),
(17, 'Glow Worm Caves Tour', 'Evening boat tour to see the Te Anau glow worm caves.', '2024-11-06 19:00:00', '2024-11-06 21:30:00', 'Te Anau Glowworm Caves', NULL),
(17, 'Milford Road Journey', 'Scenic drive along one of the world\'s most spectacular roads.', '2024-11-07 08:00:00', '2024-11-07 11:00:00', 'Milford Road', 'events/milford_road.jpg'),
(17, 'Gertrude Saddle Hike', 'Challenging alpine hike with breathtaking views of the Fiordland mountains.', '2024-11-07 12:00:00', '2024-11-07 17:00:00', 'Gertrude Saddle, Fiordland', 'events/gertrude_saddle.jpg'),
(17, 'Milford Sound Overnight Cruise', 'Overnight cruise on the majestic Milford Sound.', '2024-11-08 16:00:00', '2024-11-09 09:00:00', 'Milford Sound', NULL),

-- Journey 18: COMP639 Workshop Trip to Lincoln (8 events)
(18, 'Flight NZ5373 Wellington to Christchurch', 'Morning flight from Wellington to Christchurch.', '2025-03-15 08:00:00', '2025-03-15 09:30:00', 'Wellington to Christchurch', 'events/nz_flight.jpg'),
(18, 'Pickup from Christchurch Airport', 'Meeting classmates at the airport.', '2025-03-15 09:45:00', '2025-03-15 10:15:00', 'Christchurch Airport', NULL),
(18, 'Drive to Lincoln', 'Carpooling from Christchurch Airport to Lincoln University.', '2025-03-15 10:15:00', '2025-03-15 11:00:00', 'Christchurch to Lincoln', NULL),
(18, 'Check-in at Lincoln Motel', 'Getting settled in accommodation near campus.', '2025-03-15 11:15:00', '2025-03-15 12:00:00', 'Lincoln Motel', 'events/lincoln_motel.jpg'),
(18, 'Lunch at Coffee Culture', 'Quick lunch before the workshop begins.', '2025-03-15 12:15:00', '2025-03-15 13:00:00', 'Coffee Culture, Lincoln, NZ', NULL),
(18, 'Studio Project Workshop - Day 1', 'First day of the COMP639 workshop sessions.', '2025-03-15 13:30:00', '2025-03-15 17:30:00', 'Lincoln University', 'events/lincoln_uni.jpg'),
(18, 'Group Dinner in Lincoln', 'Dinner with classmates discussing the day\'s work.', '2025-03-15 18:30:00', '2025-03-15 20:30:00', 'Lincoln Township', NULL),
(18, 'Studio Project Workshop - Day 2', 'Final day of the workshop and project planning.', '2025-03-16 09:00:00', '2025-03-16 16:00:00', 'Lincoln University', NULL),

-- Journey 19: Aoraki/Mount Cook Exploration (5 events)
(19, 'Drive to Mount Cook Village', 'Scenic drive along Lake Pukaki to Mount Cook National Park.', '2025-01-25 08:30:00', '2025-01-25 11:30:00', 'Lake Pukaki to Mount Cook Village', 'events/pukaki_drive.jpg'),
(19, 'Hooker Valley Track', 'Stunning walk to view Aoraki/Mount Cook over glacier lakes.', '2025-01-25 13:00:00', '2025-01-25 16:30:00', 'Hooker Valley Track, Mount Cook', 'events/hooker_valley.jpg'),
(19, 'Sir Edmund Hillary Alpine Centre', 'Visit to the museum dedicated to mountaineering and Sir Edmund Hillary.', '2025-01-25 17:00:00', '2025-01-25 18:30:00', 'The Hermitage, Mount Cook Village', NULL),
(19, 'Stargazing Tour', 'Night tour in the Dark Sky Reserve with telescope viewing.', '2025-01-25 21:00:00', '2025-01-25 23:00:00', 'Mount Cook Dark Sky Reserve', NULL),
(19, 'Tasman Glacier Boat Tour', 'Boat tour on the terminal lake of New Zealand\'s largest glacier.', '2025-01-26 10:00:00', '2025-01-26 12:00:00', 'Tasman Glacier Terminal Lake', 'events/tasman_glacier.jpg'),

-- Journey 20: Stewart Island Wildlife Weekend (5 events)
(20, 'Ferry from Bluff to Oban', 'Crossing Foveaux Strait to Stewart Island/Rakiura.', '2024-12-05 09:00:00', '2024-12-05 10:30:00', 'Bluff to Oban, Stewart Island', 'events/stewart_ferry.jpg'),
(20, 'Ulva Island Bird Sanctuary', 'Predator-free island sanctuary with rare native birds.', '2024-12-05 13:00:00', '2024-12-05 16:00:00', 'Ulva Island, Stewart Island', 'events/ulva_island.jpg'),
(20, 'Kiwi Spotting Night Tour', 'Guided night walk to spot wild kiwi birds.', '2024-12-05 21:00:00', '2024-12-06 00:00:00', 'Ocean Beach, Stewart Island', NULL),
(20, 'Rakiura Track Day Walk', 'Walking a section of the Rakiura Great Walk.', '2024-12-06 09:00:00', '2024-12-06 15:00:00', 'Rakiura Track, Stewart Island', 'events/rakiura_track.jpg'),
(20, 'Fresh Seafood Dinner', 'Local blue cod and paua (abalone) dinner at a waterfront restaurant.', '2024-12-06 18:00:00', '2024-12-06 20:00:00', 'South Sea Hotel, Oban', NULL);

INSERT INTO subscriptions (
    name, duration_months, is_free_trial, discount_percent, price_nzd_excl_gst, price_nzd_incl_gst, is_admin_grantable
) VALUES
    ('Free Trial', 1, 1, 100.00, 0.00, 0.00, 0),
    ('One Month', 1, 0, 0.00, 5.22, 6.00, 0),
    ('One Quarter', 3, 0, 10.00, 14.09, 16.20, 0),
    ('One Year', 12, 0, 25.00, 46.96, 54.00, 0),
    ('Admin Gift One Month', 1, 0, 100.00, 0.00, 0.00, 1),
    ('Admin Gift One Quarter', 3, 0, 100.00, 0.00, 0.00, 1),
    ('Admin Gift One Year', 12, 0, 100.00, 0.00, 0.00, 1);

-- Insert default achievements
INSERT INTO achievements (name, description, icon_url, is_premium_only, condition_type, condition_value)
VALUES 
('Journey Beginner', 'Create your first journey', '/static/icons/journey_beginner.png', 0, 'First-time', NULL),
('Event Creator', 'Add your first event to any journey', '/static/icons/event_creator.png', 0, 'First-time', NULL),
('First Comment', 'Make your first comment on another user\'s shared event', '/static/icons/first_comment.png', 0, 'First-time', NULL),
('First Share', 'Share a journey publicly for the first time', '/static/icons/first_share.png', 0, 'First-time', NULL),
('Discovery Pioneer', 'Be the first to view another user\'s newly shared journey', '/static/icons/discovery_pioneer.png', 0, 'First-time', NULL),
('Location Explorer', 'Record events at 5 different locations', '/static/icons/location_explorer.png', 0, 'Cumulative', 5),
('Sharing Guru', 'Share 5 different journeys publicly', '/static/icons/sharing_guru.png', 0, 'Cumulative', 5),
('Popular Traveller', 'Receive 5 likes across your shared events', '/static/icons/popular_traveller.png', 0, 'Cumulative', 5),
('Long Voyager', 'Complete a journey that spans more than 30 days', '/static/icons/long_voyager.png', 0, 'One-time', 30);

