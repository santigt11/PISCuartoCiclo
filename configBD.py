import mysql.connector

def connectionBD():
    mydb = mysql.connector.connect(
        host="localhost",
        user = "root",
        password = "pis1809",
        database = "PIS"
    )
    if mydb:
        print("Conexión exitosa")
    else:
        print("Error en la conexión")
    return mydb