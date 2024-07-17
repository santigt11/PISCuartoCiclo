from configBD import connectionBD


def contarUsuarios():
    conexion_MySQL = connectionBD()
    mycursos = conexion_MySQL.cursor(dictionary=True)
    querySQL = "SELECT COUNT(*) AS total FROM PIS.Estudiantes"
    mycursos.execute(querySQL)
    return list(mycursos.fetchone().values())[0]

if __name__ == '__main__':
    print(contarUsuarios() + 10)