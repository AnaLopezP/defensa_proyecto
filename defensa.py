
def bitcoinToEuros(bitcoin_amount, bitcoin_value_euros):
    euros_value = int(bitcoin_amount)*int(bitcoin_value_euros)
    return euros_value

mybit = 300
bitcoin_value = 25291.66

myeuros = bitcoinToEuros(mybit, bitcoin_value)
print(myeuros, " euros")
