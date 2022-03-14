class Computador:
    def __int__ (self, marca, modelo):
        self.Marca=marca
        self.Modelo=modelo
        
    def __str__(self):
        computador=self.Marca+', '+self.Modelo
        return computador

Comp=Computador("HP","23X-T")
print(Comp)
