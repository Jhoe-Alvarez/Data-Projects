# 📊 Pipeline de Datos y Dashboard de Ventas Retail

Pipeline ETL completo para análisis de ventas retail con visualización interactiva en Power BI.

## 🎯 Objetivos
- Implementar pipeline ETL con Python
- Generar dataset limpio y estructurado
- Crear dashboard interactivo con KPIs de negocio

## 🛠️ Stack Tecnológico
- **Python** (Pandas, NumPy) - ETL y transformación
- **Google Colab** - Ejecución del pipeline
- **Power BI Desktop** - Dashboard y visualización

## 📂 Estructura del Proyecto
```
data-pipeline-retail/
├── data/
│   ├── raw/              # Dataset original
│   └── processed/        # Dataset procesado
├── notebook/
│   └── Retail_ETL_Colab_to_CSV.ipynb
├── dashboard/
│   └── Retail_Dashboard.pbix
└── screenshots/
    └── dashboard_overview.png
```

## 🔄 Pipeline ETL

### 1. Carga del dataset
```python
import pandas as pd
df = pd.read_csv("superstore.csv", encoding="utf-8")
print(f"Dataset cargado: {df.shape}")
```

### 2. Limpieza de columnas
```python
# Normalizar nombres de columnas
df.columns = df.columns.str.strip().str.replace(" ", "_")

# Convertir fechas
df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")
df["ShipDate"] = pd.to_datetime(df["ShipDate"], errors="coerce")

# Convertir numéricos
for col in ["Sales", "Profit", "Discount", "Quantity"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
```

### 3. Manejo de nulos y duplicados
```python
# Eliminar filas sin valores clave
df = df.dropna(subset=["OrderID", "OrderDate", "CustomerID", "ProductID", "Sales", "Quantity"])

# Rellenar nulos no críticos
df["Discount"] = df["Discount"].fillna(0)
df["Profit"] = df["Profit"].fillna(0)

# Eliminar duplicados
df = df.drop_duplicates(subset=["OrderID", "ProductID"])
```

### 4. Features adicionales
```python
import numpy as np

# Calcular precio unitario
df["UnitPrice"] = np.where(df["Quantity"] > 0, df["Sales"] / df["Quantity"], 0)

# Calcular margen porcentual
df["MarginPct"] = np.where(df["Sales"] != 0, df["Profit"] / df["Sales"], 0)

# Crear período año-mes
df["YearMonth"] = df["OrderDate"].dt.to_period("M").astype(str)
```

### 5. Exportación
```python
df.to_csv("superstore_clean.csv", index=False)
print("Dataset limpio exportado exitosamente")
```

## 📊 Dashboard - KPIs y Visualizaciones

![Dashboard Overview](screenshots/dashboard_overview.png)

### KPIs principales (Power BI DAX):
```dax
Total Sales = SUM(Sales)
Total Profit = SUM(Profit)
Total Quantity = SUM(Quantity)
Margin % = DIVIDE([Total Profit], [Total Sales])
Avg Ticket = DIVIDE([Total Sales], DISTINCTCOUNT(OrderID))
```

### Visualizaciones incluidas:
- **Tendencia temporal** - Ventas mensuales por fecha
- **Ranking de productos** - Top 10 productos más vendidos
- **Análisis de clientes** - Clientes frecuentes por ventas y órdenes
- **Distribución por categoría** - Participación en ventas
- **Filtros interactivos** - Año, Región, Categoría, Segmento

## 🚀 Uso Rápido

1. **Clonar repositorio**
   ```bash
   git clone https://github.com/tu_usuario/data-pipeline-retail.git
   ```

2. **Ejecutar ETL**
   - Abrir `Retail_ETL_Colab_to_CSV.ipynb` en Google Colab
   - Ejecutar todas las celdas

3. **Abrir Dashboard**
   - Cargar `superstore_clean.csv` en Power BI Desktop
   - Abrir `Retail_Dashboard.pbix`

## 💡 Resultados Clave
- Dataset original procesado de X filas a Y filas limpias
- Identificación de productos top performer
- Análisis de estacionalidad en ventas
- Segmentación de clientes por valor

---
**Autor:** [Tu Nombre](mailto:tuemail@correo.com) | [LinkedIn](tu-linkedin) | [GitHub](tu-github)
