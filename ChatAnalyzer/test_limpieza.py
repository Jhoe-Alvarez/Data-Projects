"""
Script de prueba para verificar la limpieza de datos mejorada
"""
from utils.data_processing import limpiar_nombre_autor, es_mensaje_sistema, es_autor_sistema

print("🧪 PRUEBAS DE LIMPIEZA DE DATOS\n")
print("=" * 60)

# Prueba 1: Limpieza de nombres con @
print("\n1️⃣ LIMPIEZA DE NOMBRES CON @:")
print("-" * 60)
nombres_test = [
    "@Juan Pérez",
    "María @González",
    "@Pedro123",
    "Ana López",
    "~Carlos~",
    "@@@Usuario"
]

for nombre in nombres_test:
    limpio = limpiar_nombre_autor(nombre)
    print(f"   {nombre:20} → {limpio}")

# Prueba 2: Detección de autores del sistema
print("\n2️⃣ DETECCIÓN DE AUTORES DEL SISTEMA:")
print("-" * 60)
autores_test = [
    ("Juan", False),
    ("cambió la foto de perfil", True),
    ("María cambió", True),
    ("salió del grupo", True),
    ("Pedro López", False),
    ("", True),
    ("añadió a Juan", True),
]

for autor, es_sistema_esperado in autores_test:
    resultado = es_autor_sistema(autor)
    icono = "✅" if resultado == es_sistema_esperado else "❌"
    print(f"   {icono} '{autor:30}' → Sistema: {resultado}")

# Prueba 3: Detección de mensajes del sistema
print("\n3️⃣ DETECCIÓN DE MENSAJES DEL SISTEMA:")
print("-" * 60)
mensajes_test = [
    ("Hola, ¿cómo estás?", False),
    ("cambió su foto de perfil", True),
    ("‎imagen omitida", True),
    ("Los mensajes están cifrados de extremo a extremo", True),
    ("Te invito a la fiesta", False),
    ("‎video omitido", True),
    ("cambió la foto del grupo", True),
    ("Cambiaste el ícono del grupo.", True),
    ("Cambiaste el icono del grupo.", True),
]

for mensaje, es_sistema_esperado in mensajes_test:
    resultado = es_mensaje_sistema(mensaje)
    icono = "✅" if resultado == es_sistema_esperado else "❌"
    print(f"   {icono} '{mensaje[:40]:40}' → Sistema: {resultado}")

# Prueba 4: Mensajes multilínea y sistema
print("\n4️⃣ LIMPIEZA DE EXPORTACIÓN REAL:")
print("-" * 60)
sample = '''3/8/2025, 12:38 a. m. - Jhoe Alvarez: No aguanto p
3/8/2025, 12:51 a. m. - Cambiaste el ícono del grupo.
3/8/2025, 12:51 a. m. - Jhoe Alvarez: Poco se habla de esa foto'''

from utils.data_processing import limpiar_chat_whatsapp

df = limpiar_chat_whatsapp(sample)
autores = df['autor'].tolist() if df is not None else []
print(f"   Filas conservadas: {len(df) if df is not None else 0}")
print(f"   Autores: {autores}")

print("\n" + "=" * 60)
print("✅ Pruebas completadas\n")
