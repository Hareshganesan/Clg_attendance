# README.md

# Student Attendance System

A comprehensive web-based system for tracking and managing student attendance using QR codes, designed to improve efficiency, reduce errors, and provide valuable insights through analytics.

## Features

- **QR Code-based Attendance**: Generate unique QR codes for each session which students can scan to mark their attendance
- **Role-based Access Control**: Different interfaces for students, faculty, and administrators
- **Analytics Dashboard**: Visualize attendance patterns and identify at-risk students
- **Cloud-based Storage**: Access attendance records anytime, anywhere
- **Offline Support**: Record attendance even without internet connectivity
- **Email Notifications**: Automated alerts for low attendance
- **Bulk Import/Export**: Easily manage large sets of student data
- **Mobile Responsive**: Use on any device

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/student-attendance-system.git
   cd student-attendance-system
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file:
   ```
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=sqlite:///attendance.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

5. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:
   ```
   python run.py
   ```

## Usage

1. **Admin**:
   - Create faculty and student accounts
   - Manage courses and enrollments
   - View analytics and reports

2. **Faculty**:
   - Create attendance sessions with QR codes
   - Monitor student attendance
   - Generate course-specific reports

3. **Students**:
   - Scan QR codes to mark attendance
   - View their attendance records
   - Receive notifications for low attendance

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy with SQLite (can be configured for PostgreSQL/MySQL)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **QR Code Generation**: qrcode library
- **Analytics**: Pandas, Plotly
- **Authentication**: Flask-Login

## License

[MIT License](LICENSE)

## Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/student-attendance-system](https://github.com/yourusername/student-attendance-system)
