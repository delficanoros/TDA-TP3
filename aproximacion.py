
def hay_adyacentes(solucion, x, y):
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            xi = x + i
            yi = y + j
            if (i != 0 or j != 0) and 0 <= xi < len(solucion) and 0 <= yi < len(solucion[0]):
                if solucion[xi][yi] == 1:
                    return True

    return False


def es_posicion_valida(matriz, barco, x, y, es_horizontal, restricciones_fils, restricciones_cols):
    if es_horizontal:
        # si no entra en la fila, no se puede agregar
        if y + barco > len(matriz[0]):
            return False

        # si el barco ocupa más de lo pedido en la restricción de la fila, no se puede agregar
        if barco > restricciones_fils[x]:
            return False

        for i in range(barco):
            if matriz[x][y + i] == 1 or hay_adyacentes(matriz, x, y + i) or restricciones_cols[y + i] <= 0:
                return False
        return True
    else:
        if x + barco > len(matriz):
            return False

        if barco > restricciones_cols[y]:
            return False

        for i in range(barco):
            if matriz[x+i][y] == 1 or hay_adyacentes(matriz, x+i, y) or restricciones_fils[x+i] <= 0:
                return False
        return True


def buscar_posicion(matriz, barco, restricciones_fils, restricciones_cols):
    if max(restricciones_fils) > max(restricciones_cols):
        for i, demanda in enumerate(restricciones_fils):
            if demanda >= barco:
                for j in range(len(matriz[0])):
                    if es_posicion_valida(matriz, barco, i, j, True, restricciones_fils, restricciones_cols):
                        return i, j, True
                    # si no lo pude insertar dependiendo de la demanda de la fila, lo salteo
    else:
        for i, demanda in enumerate(restricciones_cols):
            if demanda >= barco:
                for j in range(len(matriz)):
                    if es_posicion_valida(matriz, barco, j, i, False, restricciones_fils, restricciones_cols):
                        return j, i, False

    print("No se puede insertar")
    return -1, -1, False


def colocar_barco_y_ocupar_casilleros(matriz, barco, x, y, es_horizontal, restricciones_fils, restricciones_cols):
    if barco == 1:
        matriz[x][y] = 1
    elif es_horizontal:
        for i in range(barco):
            matriz[x][y + i] = 1
            restricciones_fils[x] -= 1
            restricciones_cols[y+i] -= 1
    else:
        for i in range(barco):
            matriz[x + i][y] = 1
            restricciones_fils[x+i] -= 1
            restricciones_cols[y] -= 1


# asumo que recibo una matriz llena de 0s
def aproximación(matriz, barcos, restricciones_fils, restricciones_cols):
    barcos.sort(reverse=True)

    for barco in barcos:  # empiezo con los de mayor tamaño
        x, y, es_horizontal = buscar_posicion(
            matriz, barco, restricciones_fils, restricciones_cols)
        if x != -1:
            colocar_barco_y_ocupar_casilleros(
                matriz, barco, x, y, es_horizontal, restricciones_fils, restricciones_cols)

    return matriz


matriz = [[0]*5 for _ in range(3)]
barcos = [2, 2, 1]
restricciones_fils = [2, 2, 1]
restricciones_cols = [1, 1, 1, 1, 1]

print(aproximación(matriz, barcos, restricciones_fils, restricciones_cols))
