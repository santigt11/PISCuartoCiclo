import mysql.connector

def connectionBD():
    mydb = mysql.connector.connect(
        host="localhost",
        user = "root",
        password = "1106017716",
        database = "PIS"
    )

    if mydb:
        print("Conexión Exitosa") 
    else:
        print("Error en la conexión con la BD")
        
    return mydb

