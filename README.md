# david_simulator
David Simulator 2018 - Work in Progress!

This is an authentic simulation of Davids life in the year 2018.

Feedback on the code is very much appreciated!

To run:

- Make sure you have the packages in requirements.txt.
- Create and run a PostgreSQL database. 
- Create config/secrets.py and assign a secret key and a database URI
```python
  secret_app_key = 'YourSecretKey'
  database_uri = 'YourPostgreSQLDatabaseUri'
```

- Run:
```
Python3.6 create_db.py
Python3.6 app.py
```

- Go to http://localhost:5000/
