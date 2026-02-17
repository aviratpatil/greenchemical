import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Parse credentials roughly or just use the known ones for this helper
# Since we know the user just confirmed 'avirat123'
try:
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="avirat123"
    )

    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS ingredients_db")
    print("Database 'ingredients_db' checked/created successfully.")
except Exception as e:
    print(f"Error creating database: {e}")
