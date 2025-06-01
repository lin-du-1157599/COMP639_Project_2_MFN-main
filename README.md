# 🌍 Journey Log - Online Travel Journal

## About the Project

Journey Log is an online travel journal platform that allows users to document their journeys, share experiences with fellow travelers, and discover new destinations through the eyes of others.



## ✨ Features

### Journey Management
- **Personal travel journal**: Create and maintain private journey records
- **Journey sharing**: Option to make journeys public for other users to view
- **Event tracking with visual memories**: Document flights, accommodations, activities, and meals
- **Location management**: Use previously entered locations to maintain consistency

### Content Discovery
- **Browse public journeys**: Explore journeys shared by other travelers
- **Search functionality**: Find journeys by title, description, or location
- **Latest updates**: View recently updated public journeys
  
### User Management
- **Multi-role system**: Travelers, Editors, and Administrators
- **Secure authentication**: User registration and login with encrypted passwords
- **Profile management**: Customize profiles with personal information and profile pictures
  
### Platform Moderation
- **Content moderation**: Editors can improve quality and remove inappropriate content
- **User management**: Admins can manage user roles and account statuses
- **Announcements**: Staff can publish platform-wide announcements (under constrcution)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/LUMasterOfAppliedComputing2025S1/COMP639_Project_1_MFN.git
   cd COMP639_Project_1_MFN
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**
   ```bash
   # Create the MySQL database
   mysql -u username -p < db/create_database.sql
   
   # Populate with sample data (optional)
   mysql -u username -p < db/populate_database.sql
   ```

5. **Set up environment variables**
   Modify the connect.py with the following:
   ```
   DB_HOST=localhost
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_NAME=journey_log
   ```

6. **Run the application**
   ```bash
   flask run
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📋 Project Structure

```
journey-log/
│
├── app/                   # Application modules
│   ├── config/            # Configuration settings
│   ├── db/                # Database scripts and connections
│   ├── routes/            # Route definitions
│   │   ├── admin.py       # Admin routes
│   │   ├── editor.py      # Editor routes
│   │   ├── event.py       # Event management routes
│   │   ├── journey.py     # Journey management routes
│   │   ├── traveller.py   # Traveler routes
│   │   └── user.py        # User authentication routes
│   ├── static/            # Static files
│   │   ├── css/           # Stylesheets
│   │   ├── images/        # Image assets
│   │   ├── js/            # JavaScript files
│   │   ├── uploads/       # User uploaded files
│   │   ├── auth_image.jpg
│   │   ├── auth_image_logo.jpg
│   │   ├── favicon.png
│   │   └── logo.png
│   ├── templates/         # HTML templates
│   │   ├── auth/          # Authentication pages
│   │   ├── base/          # Base templates
│   │   ├── event/         # Event management pages
│   │   ├── home/          # Homepage templates
│   │   ├── journey/       # Journey management pages
│   │   └── user/          # User profile pages
│   └── utils/             # Utility functions
│       ├── decorators.py  # Custom decorators
│       └── helpers.py     # Helper functions
│
├── app.py                 # Main application entry point
└── requirements.txt       # Project dependencies
```

## 🔒 User Roles

### Traveler
- Create and manage personal journeys
- View and search public journeys
- Update personal profile

### Editor
- All Traveler capabilities
- Edit public journeys for quality improvement
- Remove inappropriate content
- Manage duplicate locations
- Hide problematic journeys
- Post announcements

### Administrator
- All Editor capabilities
- Manage user roles
- Ban/unban user accounts
- Search and view all user profiles

## 🛠️ PythonAnywhere Deployment

1. **Create a PythonAnywhere account** at [www.pythonanywhere.com](https://www.pythonanywhere.com)

2. **Open a Bash console** from your PythonAnywhere dashboard

3. **Clone your repository**
   ```bash
   git clone https://github.com/LUMasterOfAppliedComputing2025S1/COMP639_Project_1_MFN.git
   ```

4. **Set up a virtual environment**
   ```bash
   cd COMP639_Project_1_MFN
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure the Web app**
   - Go to the "Web" tab in PythonAnywhere
   - Click "Add a new web app"
   - Choose "Manual configuration" and select Python 3.8
   - Set the path to your project directory
   - Configure WSGI file to point to your `app.py` file

6. **Set up the database**
   - Go to the "Databases" tab
   - Create a new MySQL database
   - Use the MySQL console to run your schema and data SQL files

7. **Configure environment variables**
   - Edit the WSGI configuration file to include your environment variables

8. **Reload your web app** to apply all changes

## 📝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under Lincoln University guidelines.

## 👥 Team

Listed alphabetically by surname:

- Lin Du (Alan) (Student ID No.: 1157599)
- Min Hu (Vincent) (Student ID No.: 1163417)
- Peng-Yu Liu (Agnes) (Student ID No.: 1164384) 
- Xiaoxuan Wei (Serena) (Student ID No.: 1161823)
- Rong Zhou (Cruise) (Student ID No.: 1162346)
