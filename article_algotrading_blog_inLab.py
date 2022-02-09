import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas_datareader.data as wb

### Obtenim les dades historique de tancament de FAES FARMA (ticker a Yahoo: FAE.MC)
data = wb.DataReader('FAE.MC', 'yahoo', '2016-1-1')

### Establim el número de dies per a la mitjana curta i per a la mitjana llarga
short_window = 15
long_window = 150


### Calculem les dues mitjanes per cadascun dels dies
data['short']= data['Adj Close'].rolling(short_window).mean()
data['long']= data['Adj Close'].rolling(long_window).mean()

### A la columna signal  posarem un 1 si la mitjana curta està per damunt de la llarga
data['signal'] = np.where(data['short'] > data['long'], 1, 0)

### A la columna position  marquem quan hi ha un canvi, implicarà quan hi haurà
### una compra (+1)  o una venda (-1)

data['position'] = data['signal'].diff()

### Establim com a capital inicial 2000 eurs
###  i per fer-ho senzill, sempre comprarem 1000 accions
capital = 3000
stocks = int(1000)

###  Afegim una columna amb el número d'accions que tindrem a la cartera en cadascun dels dies
data['num_accions_a_cartera'] = stocks * data['signal']

###  Afegim una columna amb el valor de la cartera que tindrem cadascun dels dies
data['valor_de_la_cartera'] = data['num_accions_a_cartera'] .multiply(data['Adj Close'])

###  Afegim una columna amb el diferencial d'accions respecte el dia anterior
data['num_accions_a_cartera_diff'] = data['num_accions_a_cartera'] .diff()

###  Afegim una columna amb el cash que tindrem cadascun dels dies
data['cash'] = capital - (data['num_accions_a_cartera_diff'].multiply(data['Adj Close']).cumsum())

###  Afegim una columna amb l'import total que tindrem: cash + valor de les accions
data['total'] = data['cash'] + data['valor_de_la_cartera']

# Eliminem les files que tenen algun valor que no s'hagi pogut calcular
data.dropna(inplace=True)


print("\n Valor total brut de la cartera al final del període:", round(data['total'].iloc[-1],2))

############################################################
###   GRAFIQUEM ELS RESULTATS
############################################################

### Preparem una figura quadrada de 2 fles i una columns
grafico = plt.figure(figsize=(20,20))
tabla = gridspec.GridSpec(nrows=2, ncols=1, figure=grafico, height_ratios=[1,1])

graf_sup = plt.subplot(tabla[0,0])
graf_inf = plt.subplot(tabla[1,0])


### Gràfica superior amb el preu de tancament
data['Adj Close'].plot(ax=graf_sup, lw=2., color='k')

### Gràfica superior amb les marques d'on comprem / venem
graf_sup.plot(data[data['position'] == 1]['Adj Close'], '^', markersize=15, color='g')
graf_sup.plot(data[data['position'] == -1]['Adj Close'], 'v', markersize=15, color='r')

### Gràfica superior amb les mitjanes llarga i curta
data[['short', 'long']].plot(ax=graf_sup, lw=1.3)

## Li posem el títol
graf_sup.set_title("Preu de l'acció de l'empresa Faes Farma")

### Gàfica inferior amb el valor de la cartera en cada moment
graf_inf.set_title("Valor de la cartera amb un capital inicial de " + str(capital) + " euros")
data['total'].plot(ax=graf_inf, lw=2.)

### Gràfica inferior amb les marques d'on comprem / venem
graf_inf.plot(data[data['position'] == 1]['total'], '^', markersize=15, color='g')
graf_inf.plot(data[data['position'] == -1]['total'], 'v', markersize=15, color='r')

## Mostrem les gràfiques
plt.grid()
plt.show()