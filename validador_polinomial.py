def hay_adyacentes(solucion, casilleros_visitado, x, y):
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            xi = x + i
            yi = y + j

            if xi != 0 or yi != 0:
                if 0 <= xi and xi < len(solucion) and 0 <= yi and yi < len(solucion[0]):
                    if solucion[xi][yi] == 1 and not casilleros_visitado[xi][yi]:
                        return True

    return False


def es_barco_valido(x, y, solucion, casilleros_visitados, long_barco, es_horizontal):
    if long_barco == 1:
        return True
    elif es_horizontal:
        for i in range(long_barco):
            if solucion[x][y+i] == 0 or casilleros_visitados[x][y+i] or y + i >= len(solucion[0]):
                return False
            if hay_adyacente(solucion, casilleros_visitados, x, y+i):
                return False
            casilleros_visitados[x][y+i] = True
    else:
        for i in range(long_barco):
            if solucion[x+i][y] == 0 or casilleros_visitados[x+i][y] or x + i >= len(solucion):
                return False
            if hay_adyacente(solucion, casilleros_visitados, x+i, y):
                return False
            casilleros_visitados[x+i][y] = True

    return True
            

def validador(matriz, barcos, restricciones_fil, restricciones_col, solucion):
    if len(matriz) != len(solucion) or len(matriz[0]) != len(solucion[0]):
        return False

    fils = len(solucion)
    cols = len(solucion[0])

    for i in range(fils):
        if sum(solucion[i]) != restricciones_fil[i]: # la cantidad de casilleros ocupados por la fila k es distinta a la especificada en la restriccion
            return False
        
    for j in range(cols):
        casilleros_ocupados_cols = sum(solucion[i][j] for i in range(fils))
        if casilleros_ocupados_cols != restricciones_col[j]:
            return False
        
    
    casilleros_visitado = [[False] * cols for _ in range(fils)]
    barcos_no_visitados = barcos[:] #verifico que todos los barcos solicitados esten en la solucion

    for i in range(fils):
        for j in range(cols):
            if solucion[x][y] == 1 and  not casilleros_visitado[i][j]:
                casilleros_visitado[i][j] = True
                es_horizontal = False 
                long_barco = 1
                
                if j+1 < fils and solucion[i][j+1] == 1:
                    while j + long_barco < fils and solucion[i][j+long_barco] == 1: #calculo la longitud del barco actual
                        long_barco += 1
                elif i+1 < cols and solucion[i+1][j] == 1:
                    es_horizontal = True
                    while i + long_barco < cols and solucion[i+long_barco][j] == 1:
                        long_barco += 1

                if long_barco not in barcos_no_visitados or not es_barco_valido(i,j, solucion, casilleros_visitado, long_barco,es_horizontal):
                    return False
                
                barcos_no_visitados.remove(long_barco)

    if len(barcos_no_visitados) != 0:
        return False
    
    return True