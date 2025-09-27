# Notes-App


A simple Flask + SQLite web app for creating, editing, and managing personal notes.
It supports user signup, login (with JWT authentication), and CRUD operations on notes.



User authentication (JWT-based login, signup, logout)
Create, read, update, delete (CRUD) notes
Simple UI with popup modal for adding/editing notes
SQLite database with SQLAlchemy models






Design Decisions & Trade-offs

JWT over session cookies → stateless authentication, avoids storing sessions in Flask.
SQLite → lightweight DB for local development. Easy to swap with PostgreSQL/MySQL later.
jQuery AJAX → used for simplicity in handling signup/login/notes CRUD without page reloads




External Resources Used

Flask Documentation
 – framework reference

SQLAlchemy ORM
 – database modeling

PyJWT
 – JSON Web Token handling

jQuery AJAX