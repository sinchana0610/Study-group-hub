📚 Study Group Hub

A Flask-based web application that lets students create, join, and manage study groups.
The project supports user authentication, group management, and dynamic content rendering with Jinja2 templates.

🚀 Features

🔑 User Authentication — Register, login, logout

👥 Study Groups — Create, view, and manage study groups

📄 Templates — Clean UI built with Jinja2 & Bootstrap/CSS

💾 Database — SQLite support (via create_db.py)

🎨 Custom Styling — Basic design in static/style.css

📂 Project Structure
Study-group-hub/
├─ app.py              # Main Flask app (routes, logic)
├─ create_db.py        # Script to create database & tables
├─ requirements.txt    # Python dependencies
├─ static/
│   └─ style.css       # Custom styles
└─ templates/
    ├─ base.html
    ├─ index.html
    ├─ login.html
    ├─ register.html
    ├─ group.html
    └─ create_group.html

⚙️ Installation
1. Clone this repository
git clone https://github.com/sinchana0610/Study-group-hub.git
cd Study-group-hub

2. Create virtual environment
python -m venv .venv
# Activate:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Initialize database
python create_db.py

5. Run the application
python app.py


Now open http://127.0.0.1:5000/
 in your browser.

🖥️ Usage

Register a new account

Log in with your credentials

Create a new study group or view existing ones

Manage your groups (view members, group info, etc.)

🌟 Future Enhancements

Group sessions/events scheduling

File sharing inside groups

Search/filter groups by subject or tags

Email notifications for group invites

🤝 Contributing

Fork this repo

Create a new branch (git checkout -b feature-name)

Commit your changes (git commit -m "Added new feature")

Push to branch (git push origin feature-name)

Open a Pull Request

📜 License

This project is open-source and available under the MIT License.
