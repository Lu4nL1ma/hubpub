from django.test import TestCase

# Create your tests here.

import pandas as pd

# Criando um exemplo rápido
dados = {
    'A': [10, 20, 10, 40],
    'B': ['Alpha', 'Beta', 'Gamma', 'Delta'],
    'C': ['Red', 'Blue', 'Green', 'Yellow'],
    'D': [10, 12, 13, 14]
}
df = pd.DataFrame(dados)

# Condição: Se A for maior que 25, pegue B e C
# O .loc funciona como: df.loc[linhas, colunas]
resultado = df.loc[df['A'] == 10, ['B', 'C', 'D']]



print(resultado)