# Database Lab 2: Login & To-Do Application

## Student information 
- Student name: Mohamed Nader Kamal Elashry
- Student ID: 2304082
- Contributions: I worked alone and completed all parts of the project.


## Technologies
Python / Flask, PyMySQL (plain SQL, no ORM), bcrypt, Flask-Session , HTML, CSS, JavaScript, and MySQL 8.0. MySQL Workbench runs the database script; Python runs the website.

## Windows setup, step by step
1. Install Python 3 with pip, MySQL Server 8.0 and MySQL Workbench. 
2. Open Workbench and connect to localhost:3306 using my MySQL username and password.
3. Select **File > Open SQL Script**, open `database/schema.sql`, and click the lightning bolt to execute the whole script. **This script drops and recreates registration: rerunning it deletes its existing data.** Refresh SCHEMAS; expand registration > Tables. You should see users and todos. The submitted script contains DDL only, no sample data.
4. In a Windows Command Prompt inside this project folder, run:
   ```bat
   py -3.13 -m venv .venv
   .venv\Scripts\activate
   python -m pip install -r requirements.txt
   copy .env.example .env
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
5. Edit `.env`: enter your own MySQL password in DB_PASSWORD and paste the generated random value into SECRET_KEY. Keep DB_NAME=registration and DB_PORT=3306. Quote a password containing `#` in the .env file. Never commit .env.
6. Start the website:
   ```bat
   python app.py
   ```
7. Open http://127.0.0.1:5000/register in the browser. Register an account, then add tasks. Workbench is used to inspect the tables, while the browser is used to register, log in and manage tasks.
8. Stop the server with Ctrl+C. For a later run, activate the virtual environment and run `python app.py` again. 

## Features R1-R10
- R1: Registration, duplicate-email feedback and automatic login.
- R2: Login with one common error for unknown emails and wrong passwords; 
- R3: Private to-do list, belonging to the session user, newest first.
- R4-R7: Add, edit, save done/open status, and delete after confirmation.
- R8: Browser and server validation with the required exact messages.
- R9: password hashing, parameterized SQL, and ownership checks.
- R10: consistent styling and a responsive layout

## Required screenshots 
Put these four images in screenshots
1. Register page after submitting an empty form, showing all four messages.



## Manual checks
Done

## GitHub submission
https://github.com/mn3546639-gif/db-lab2-mohamed-nader

## Verification note
The application was connected successfully to MySQL on Windows using Python 3.13. Registration, adding tasks, and saving a task as completed were verified.
