import dask.dataframe as dk
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeRegressor, plot_tree, export_graphviz, export_text
from sklearn.metrics import mean_squared_error
import warnings
import matplotlib.pyplot as plt

f = dk.read_csv(os.path.join("/TRABAJO FINAL/air_traffic_data.csv")).compute()
f.head()

f.tail()

f.dtypes

a = f['Operating Airline'].unique()
for i in range(len(a)):
  print(a[i])

print(len(a))

gb = f.groupby(by = "Operating Airline") #En esta linea juntamos todos los valores con la misma compañía aérea
gb_medias = gb["Passenger Count"].mean() #Hacemos la media de los valores juntados, solamente en la columna de pasajeros

for i in range(len(gb_medias)):
  print("Compañía: ", gb_medias.index[i], "Media de pasajeros: ", gb_medias[i])

gb_region = f.groupby(by = "GEO Region")
gb_region_max = gb_region["Passenger Count"].max()

print(gb_region_max)
print(gb_region_max.index)

save_f = f #copia de seguridad

tabla_borrar = []
for i in range(len(gb_region_max)): 
  #Comparo la serie gb_region_max con el dataframe original, añadiendo en p sólo los que no cumplan la condición:
  p = (f[(f["GEO Region"]==  str(gb_region_max.index[i])) & (f["Passenger Count"] < gb_region_max.values[i])]) 
  tabla_borrar.append(p.index.values) #Añado en tabla_borrar los índices de esos registros.

lista_borrar = []
for i in range(len(tabla_borrar)):
  lista_borrar.append(tabla_borrar[i].tolist()) #Añado en la lista los arrays con índices transformados a listas
  save_f = save_f.drop(lista_borrar[i]) #Cojo cada lista y se la paso a drop para que elimine las filas correspondientes

f_maxpass = save_f.to_csv(sep = ",", index = True)
print(f_maxpass)

f_medias = gb_medias.to_csv(sep = ",", index = True)
print(f_medias)

#QUITAR COLUMNAS REPETIDAS
columnas_borrar = ["Published Airline", "Published Airline IATA Code", "Activity Type Code", "Passenger Count"] #Las borro porque dan información rebundante.
f.drop(columnas_borrar, axis = 1, inplace = True)
f

#TRANSFORMO LA COLUMNA MES EN ESTACIONES PARA CONSEGUIR MÁS INFORMACIÓN RELEVANTE 
cambiar_mes = {"January": 0, "February": 0, "March": 1, "April": 1, "May": 1, 
               "June": 2, "July": 2, "August": 2, "September": 3, "October": 3, 
               "November": 3, "December": 0}
f["Month"].replace(cambiar_mes, inplace = True)
#CAMBIO EL NOMBRE DE LA COLUMNA MES A ESTACIÓN
f.rename(columns = {'Month': 'Season'}, inplace = True)
#MIRO EL NUMERO DE PASAJEROS POR ESTACIÓN
f_estaciones = f.groupby(by = "Season")
f_estaciones_pasajeros = f_estaciones["Adjusted Passenger Count"].sum()
f_estaciones_pasajeros

f

cambiar_act2 = {'Deplaned': 0, 'Enplaned': 1, 'Thru / Transit * 2': 2}
cambiar_precio = {"Low Fare": 0, "Other": 1}
cambiar_geosum = {'Domestic': 0, 'International': 1}

def remplazar_y_media(dicc, columna):
   f[columna].replace(dicc, inplace = True)
   media = f[columna].mean()
   return media

#MEDIA PASAJEROS
#media_pass = f["Passenger Count"].mean()

#MEDIA AÑO
media_year = f["Year"].mean()

#MEDIA MES
media_mes = f["Season"].mean()

#MEDIA PASAJEROS AJUSTADO
media_passajus = f["Adjusted Passenger Count"].mean()

#MEDIA ACTIVIDAD TIPO 
media_tipo2 = remplazar_y_media(cambiar_act2, 'Adjusted Activity Type Code')

#PRECIO
media_precio = remplazar_y_media(cambiar_precio, 'Price Category Code')

#ACTIVIDAD TIPO
#media_tipo = remplazar_y_media(cambiar_act, "Activity Type Code")

#GEO SUMMARY
media_geosum = remplazar_y_media(cambiar_geosum, 'GEO Summary')

#ACTIVITY PERIOD
media_periodo = f['Activity Period'].mean()

print("-----MEDIAS------")
#print("Passenger Count: ", media_pass)
print("Adjusted Passenger Count: ", media_passajus)
print("Year: ", media_year)
print("Season: ", media_mes)
#print("Activity Type Code: ", media_tipo)
print('Adjusted Activity Type Code: ', media_tipo2)
print('Price Category Code: ', media_precio)
print('GEO Summary: ', media_geosum)

#DESVIACONES TÍPICAS
#std_pass = f["Passenger Count"].std()
std_passajus = f["Adjusted Passenger Count"].std()
std_year = f["Year"].std()
std_mes = f["Season"].std()
#std_tipo = f["Activity Type Code"].std()
std_tipo2 = f["Adjusted Activity Type Code"].std()
std_precio = f["Price Category Code"].std()
std_geosum = f["GEO Summary"].std()

print("-----------DESVIACIONES TÍPICAS-----------")
#print("Passenger Count: ", std_pass)
print("Adjusted Passenger Count: ", std_passajus)
print("Year: ", std_year)
print("Season: ", std_mes)
#print("Activity Type Code: ", std_tipo)
print('Adjusted Activity Type Code: ', std_tipo2)
print('Price Category Code: ', std_precio)
print('GEO Summary: ', std_geosum)

f.corr(numeric_only = True)

#ARBOL DE REGRESIÓN
warnings.filterwarnings('once')
ff = f #copia seguridad porque voy a robar columnas
ff = ff.drop(["Operating Airline", "Operating Airline IATA Code", 
              "GEO Region", "Terminal", "Boarding Area"], axis = 1)

#divido el dataset en train y test
X_train, X_test, Y_train, Y_test = train_test_split(ff.drop(columns = "GEO Summary"), 
                                                    ff["GEO Summary"], 
                                                    random_state = 123)

#Creación del modelo
modelo = DecisionTreeRegressor(max_depth= 3, random_state= 123)

#Entreno el modelo
modelo.fit(X_train, Y_train)

#Representación del arbol
fig, ax = plt.subplots(figsize = (12, 5))

print("PROFUNDIDAD DEL ARBOL: ", modelo.get_depth())
print("NUMERO DE NODOS TERMINALES (HOJAS): ", modelo.get_n_leaves())

plot = plot_tree(decision_tree= modelo, 
                 feature_names = ff.drop(columns = "GEO Summary").columns,
                 class_names = "GEO Summary", 
                 filled = True,
                 impurity = False, 
                 fontsize = 10,
                 precision = 2,
                 ax = ax)

import random

def bitcoinToEuros(bitcoin_amount, bitcoin_value_euros):
    euros_value = int(bitcoin_amount)*int(bitcoin_value_euros)
    return euros_value

bitcoin_value = 25291.66 
lisssbit = []
myeuros = []
for i in range(len(f)):
  a = random.randint(0, 300)
  lisssbit.append(a)
  myeuros.append(bitcoinToEuros(lisssbit[i], bitcoin_value))

#Añado una columna llamada bitcoin al csv

f["Bitcoin"] = myeuros
f

#Hago una matriz de correlación con mi valor de bitcoin 
f.corr(numeric_only = True)