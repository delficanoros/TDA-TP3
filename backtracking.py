def hay_adyacentes(solucion, x, y):
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            xi = x + i
            yi = y + j
            if (i != 0 or j != 0) and 0 <= xi < len(solucion) and 0 <= yi < len(solucion[0]):
                if solucion[xi][yi] == 1:
                    return True

    return False


def se_puede_ubicar(matriz, fil, col, largo, orientacion, restricciones_fil, restricciones_col):
    n, m = len(matriz), len(matriz[0])
    if (orientacion == "horizontal" and col + largo > m) or (orientacion == "vertical" and fil + largo > n):
        return False

    if hay_adyacentes(matriz, fil, col):
        return False

    if orientacion == "horizontal":
        if sum(matriz[fil]) + largo > restricciones_fil[fil]:
            return False
        for i in range(largo):
            if sum(matriz[r][col + i] for r in range(n)) + 1 > restricciones_col[col + i]:
                return False
    elif orientacion == "vertical":
        if sum(matriz[r][col] for r in range(n)) + largo > restricciones_col[col]:
            return False
        for i in range(largo):
            if sum(matriz[fil + i]) + 1 > restricciones_fil[fil + i]:
                return False

    return True


def actualizar_posicion_matriz(matriz, i, j, largo, orientacion, value):
    for k in range(largo):
        fil, col = (i, j + k) if orientacion == "horizontal" else (i + k, j)
        matriz[fil][col] = value


def calcular_demanda(matriz, restricciones_fil, restricciones_col):
    n, m = len(matriz), len(matriz[0])
    suma_filas = sum(
        [sum(matriz[i]) for i in range(n)])
    suma_columnas = sum(
        [sum(matriz[i][j] for i in range(n)) for j in range(m)])
    total_filas = sum(restricciones_fil)
    total_cols = sum(restricciones_col)
    demanda_llena = suma_columnas + suma_filas
    demanda_total = total_filas + total_cols
    return demanda_llena, demanda_total


def batalla_naval(matriz, barcos, restricciones_fil, restricciones_col):
    barcos = sorted(barcos, reverse=True)  # ordeno para mejorar la complejidad
    posiciones = [None] * len(barcos)
    mejor_solucion = matriz
    return batalla_naval_bk(matriz, barcos, restricciones_fil, restricciones_col, 0, posiciones, mejor_solucion, 0, posiciones)


def batalla_naval_bk(matriz, barcos, restricciones_fil, restricciones_col, index, posiciones, mejor_solucion, mejor_demanda, mejor_posiciones):
    demanda_parcial, _ = calcular_demanda(
        matriz, restricciones_fil, restricciones_col)
    if index == len(barcos):
        if demanda_parcial > mejor_demanda:
            return demanda_parcial, [col[:] for col in matriz], posiciones[:]
        return mejor_demanda, mejor_solucion, mejor_posiciones

    if index > len(barcos):
        return mejor_demanda, mejor_solucion, mejor_posiciones

    if demanda_parcial + sum(barcos[i] for i in range(index, len(barcos))) < mejor_demanda:
        return mejor_demanda, mejor_solucion, mejor_posiciones

    largo_barco = barcos[index]
    for i in range(len(matriz)):
        for j in range(len(matriz[0])):
            if matriz[i][j] == 1:
                continue
            for orientacion in ["horizontal", "vertical"]:
                if se_puede_ubicar(matriz, i, j, largo_barco, orientacion, restricciones_fil, restricciones_col):
                    posiciones[index] = (
                        (i, j), (i + largo_barco - 1, j) if orientacion == "vertical" else (i, j + largo_barco - 1))

                    actualizar_posicion_matriz(
                        matriz, i, j, largo_barco, orientacion, 1)

                    posible_demanda, posible_solucion, posible_posiciones = batalla_naval_bk(
                        matriz, barcos, restricciones_fil, restricciones_col, index + 1, posiciones, mejor_solucion, mejor_demanda, mejor_posiciones)
                    if posible_demanda > mejor_demanda:
                        mejor_demanda = posible_demanda
                        mejor_solucion = posible_solucion
                        mejor_posiciones = posible_posiciones

                    actualizar_posicion_matriz(
                        matriz, i, j, largo_barco, orientacion, 0)
                    posiciones[index] = None

    posible_demanda2, posible_solucion2, posible_posiciones2 = batalla_naval_bk(
        matriz, barcos, restricciones_fil, restricciones_col, index + 1, posiciones, mejor_solucion, mejor_demanda, mejor_posiciones)
    if posible_demanda2 > mejor_demanda:
        mejor_demanda = posible_demanda2
        mejor_solucion = posible_solucion2[:]
        mejor_posiciones = posible_posiciones2[:]

    return mejor_demanda, mejor_solucion, mejor_posiciones
