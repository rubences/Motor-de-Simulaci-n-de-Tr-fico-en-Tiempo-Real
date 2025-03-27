# simulacion_trafico/ui/gui.py

import tkinter as tk

class SimulationCanvasGUI:
    def __init__(self, simulator, update_interval=50):
        """
        Inicializa la interfaz gráfica en un Canvas.
        
        Args:
            simulator: Instancia del simulador que debe proveer acceso a la ciudad,
                       donde se encuentran las listas de vehículos y semáforos.
            update_interval: Intervalo de actualización en milisegundos.
        """
        self.simulator = simulator
        self.update_interval = update_interval  # milisegundos

        self.root = tk.Tk()
        self.root.title("Simulación de Tráfico en Tiempo Real")

        # Definimos un Canvas para dibujar el entorno
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="lightgray")
        self.canvas.pack()

        # Diccionarios para guardar las referencias a los elementos gráficos
        self.vehicle_items = {}       # clave: id del vehículo, valor: objeto canvas
        self.traffic_light_items = {} # clave: id del semáforo, valor: objeto canvas

        # Posiciones fijas para semáforos en la GUI (puedes ajustar según tu escenario)
        self.traffic_light_positions = {
            "T1": (100, 100),
            "T2": (300, 100),
            # Agrega más asignaciones si tienes más semáforos
        }

    def update_canvas(self):
        """
        Actualiza el Canvas dibujando o moviendo los vehículos y cambiando el color de los semáforos.
        """
        # --- Actualizar semáforos ---
        for tl in self.simulator.city.traffic_lights:
            # Obtener posición definida para el semáforo (si no se encuentra, usar posición por defecto)
            pos = self.traffic_light_positions.get(tl.id_, (50, 50))
            x, y = pos
            radio = 15

            # Seleccionar el color según el estado actual del semáforo
            if tl.current_state == "GREEN":
                color = "green"
            elif tl.current_state == "YELLOW":
                color = "yellow"
            else:
                color = "red"

            if tl.id_ in self.traffic_light_items:
                # Actualizar color del semáforo ya dibujado
                self.canvas.itemconfig(self.traffic_light_items[tl.id_], fill=color)
            else:
                # Dibujar el semáforo como un círculo
                item = self.canvas.create_oval(x - radio, y - radio, x + radio, y + radio,
                                               fill=color, outline="black", width=2)
                self.traffic_light_items[tl.id_] = item

        # --- Actualizar vehículos ---
        for v in self.simulator.city.vehicles:
            # Suponemos que v.position es una tupla (x, y) en coordenadas de la GUI
            x, y = v.position
            ancho = 20
            alto = 10
            # Calculamos las coordenadas del rectángulo centrado en (x, y)
            x1, y1 = x - ancho / 2, y - alto / 2
            x2, y2 = x + ancho / 2, y + alto / 2

            # Usamos un color fijo para los vehículos (puedes mejorar para distinguir tipos o direcciones)
            color = "blue"

            if v.id_ in self.vehicle_items:
                # Actualizamos la posición del vehículo ya dibujado
                self.canvas.coords(self.vehicle_items[v.id_], x1, y1, x2, y2)
            else:
                # Dibujamos el vehículo y guardamos la referencia
                item = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                self.vehicle_items[v.id_] = item

        # Programamos la siguiente actualización
        self.root.after(self.update_interval, self.update_canvas)

    def run(self):
        """
        Inicia el ciclo principal de Tkinter.
        """
        self.update_canvas()
        self.root.mainloop()


def launch_gui(simulator):
    """
    Función para lanzar la GUI.
    Se debe invocar desde el hilo principal, mientras la simulación se ejecuta en otro hilo.
    
    Args:
        simulator: Instancia del simulador.
    """
    gui = SimulationCanvasGUI(simulator)
    gui.run()


