# simulacion_trafico/ui/gui.py

import tkinter as tk

class SimulationGUI:
    def __init__(self, simulator, update_interval=1000):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            simulator: Instancia del simulador que debe proveer el método get_snapshot().
            update_interval: Intervalo de actualización en milisegundos.
        """
        self.simulator = simulator
        self.update_interval = update_interval  # en milisegundos

        self.root = tk.Tk()
        self.root.title("Simulación de Tráfico en Tiempo Real")

        # Creamos un widget Text para mostrar el estado de la simulación
        self.text_widget = tk.Text(self.root, width=80, height=20, font=("Arial", 12))
        self.text_widget.pack(padx=10, pady=10)

    def update_gui(self):
        """
        Actualiza el contenido del widget de texto con el estado actual de la simulación.
        """
        # Se obtiene el snapshot de la simulación
        snapshot = self.simulator.get_snapshot()
        # Limpiamos el widget
        self.text_widget.delete("1.0", tk.END)
        # Insertamos el estado de semáforos y vehículos
        self.text_widget.insert(tk.END, "--- Estado Actual de la Simulación ---\n")
        self.text_widget.insert(tk.END, "Semáforos:\n")
        for tl_info in snapshot["traffic_lights"]:
            self.text_widget.insert(tk.END, f"  {tl_info}\n")
        self.text_widget.insert(tk.END, "\nVehículos:\n")
        for v_info in snapshot["vehicles"]:
            self.text_widget.insert(tk.END, f"  {v_info}\n")
        # Programamos la siguiente actualización
        self.root.after(self.update_interval, self.update_gui)

    def run(self):
        """
        Inicia el ciclo principal de Tkinter.
        """
        self.update_gui()  # Inicia la primera actualización
        self.root.mainloop()

def launch_gui(simulator):
    """
    Función para lanzar la GUI. Se debe invocar desde el hilo principal.
    
    Nota: Para que la simulación y la interfaz gráfica funcionen de forma concurrente,
    la lógica de la simulación (por ejemplo, un bucle asíncrono) debe ejecutarse en otro hilo
    o proceso. Esto garantiza que el mainloop de Tkinter no se bloquee.
    """
    gui = SimulationGUI(simulator)
    gui.run()

