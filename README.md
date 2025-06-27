
Masterschool Final Backend Project



# ScrumPal
A lightweight agile project management tool built with FastAPI and PostgreSQL – perfect for small teams that want to self-host.


## ✨ Features

- 🧑‍💼 User registration & JWT-based authentication
- 📁 Project and task management
- 👥 Assign team members to projects
- 📦 RESTful API built with FastAPI(Pydantic) and PostgrSQL
- 🛠️ SQLAlchemy & Alembic for database models and migrations


## 🚀 Installation

```bash
git clone https://github.com/Unger1981/ScrumPal
cd myproject
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

!!! Docker image provided soon !!!



### 4. ⚙️ Configuration
Guide for environment variables:
```markdown
## ⚙️ Configuration

Create a `.env` file in the project root with the following content:

DATABASE_URL=postgresql://user:password@localhost:5432/myproject
SECRET_KEY=your_secret_key




### 5. ▶️ Running the App
```markdown
## ▶️ Running the App

```bash
uvicorn app.main:app --reload


### 7. 🛠️ Tech Stack
```markdown
## 🛠️ Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [JWT](https://jwt.io/)

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

1. Fork the project
2. Create your branch: `git checkout -b feature/xyz`
3. Commit your changes: `git commit -m 'Add xyz feature'`
4. Push to your branch: `git push origin feature/xyz`
5. Open a pull request


## 📬 Contact

https://github.com/Unger1981 😃  📞📞📞📞


## 🚧 Further Implementations

1. **Testing**  
   Add automated unit tests, integration tests, and end-to-end tests to ensure reliability and catch regressions early.

2. **Email Client for Password Reset (OTP)**  
   Implement a secure email service to handle password reset flows, including generating and verifying One-Time Passwords (OTP).

3. **Two-Factor Authentication (2FA)**  
   Add optional 2FA for stronger account security, e.g., via authenticator apps or SMS.

4. **Docker**  
   Containerize the application with Docker for easier deployment and environment consistency.
