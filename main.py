import client.consulta

class Main:
    def __init__(self):
        self.consulta = client.consulta.Consulta()
        print()

    def start(self):
        self.consulta.consulta('1027408-36.2018.4.01.3400')

Main().start()