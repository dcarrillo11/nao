import pandas as pd
import random

# Número de participantes
num_participants = 30

# Pruebas
tests = ['Video', 'Realidad Virtual', 'Robot']

# Crear una lista para almacenar el orden de pruebas de cada participante
order_data = []

# Generar el orden aleatorio de pruebas para cada particsipante
for participant in range(1, num_participants + 1):
    random_order = random.sample(tests, len(tests))  # Genera un orden aleatorio
    order_data.append([participant] + random_order)

# Crear un DataFrame de pandas
df = pd.DataFrame(order_data, columns=["Participante", "Prueba 1", "Prueba 2", "Prueba 3"])

# Guardar el DataFrame en un archivo Excel
output_path = "./orden_pruebas_participantes.xlsx"
df.to_excel(output_path, index=False)

output_path
