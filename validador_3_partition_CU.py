def unario_a_decimal(S, solucion):
    S_aux = [str(i).count('1') for i in S]
    solucion_aux = []
    for subconjunto in solucion:
        sub = [str(i).count('1') for i in subconjunto]
        solucion_aux.append(sub)
    return S_aux, solucion_aux


def validador(S, solucion):
    if len(solucion) != 3:
        return False

    S_aux, solucion_aux = unario_a_decimal(S, solucion)

    suma1 = sum(solucion_aux[0])
    suma2 = sum(solucion_aux[1])
    suma3 = sum(solucion_aux[2])
    suma_total = sum(S_aux) / 3

    if suma1 != suma2 or suma1 != suma3 or suma2 != suma3:
        return False
    if suma_total != suma1:  # con que uno tenga la misma suma, todos suman lo mismo
        return False

    vistos = []  # utilizo un vector para permitir repetidos
    for subconjunto in solucion_aux:
        for i in subconjunto:
            if i not in S_aux:
                return False
            vistos.append(i)

    if len(vistos) != len(S_aux):
        return False

    return True
