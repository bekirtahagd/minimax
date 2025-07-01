import copy
import graphviz
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import TextBox

class TicTacToe:
    def __init__(self):
        self.zug_nr = 0  # Für Nummerierung der PNG-Dateien
        self.max_visuelle_tiefe = 3  # Visualisierungstiefe, kann angepasst werden

    def tic_Tac_toe(self):
        spielfeld = [[" " for _ in range(3)] for _ in range(3)] # Leeres 3x3-Spielfeld
        
        # Den beginnenden Spieler festlegen
        aktueller_spieler = ""
        while aktueller_spieler not in ["X", "O"]:
            aktueller_spieler = input("Wer möchte beginnen? (X: Du  | O: KI): ").upper()

        # Die Game-Loop
        while True:
            # Zuerst wird das leere Spielfeld ausgegeben
            self.spielfeld_ausgeben(spielfeld)

            # Falls der Spieler dran ist
            if aktueller_spieler == "X":
                # Zug vom Spieler wird abgefragt
                print(f"Spieler {aktueller_spieler}, gib deinen Zug ein (Format: Reihe Spalte (?max_visuelle_tiefe), z.B. 1 1 = oben links): ")
                eingabe = input("Gib Reihe Spalte [max_tiefe] ein: ").split()

                if len(eingabe) < 2:
                    print("Fehler: Mindestens Reihe und Spalte angeben!")
                    continue

                reihe = int(eingabe[0]) - 1
                spalte = int(eingabe[1]) - 1
                if len(eingabe) > 2:
                    self.max_visuelle_tiefe = int(eingabe[2])

                # Prüfen ob der Spieler einen korrekten Zug macht, oder ob der Input falsch ist
                if reihe not in [0, 1, 2] or spalte not in [0, 1, 2] or spielfeld[reihe][spalte] != " ":
                    print("Dieser Zug ist nicht erlaubt. Bitte versuche es erneut.")
                    continue
                
                # Zug wird gesetzt
                spielfeld[reihe][spalte] = aktueller_spieler

                # Ki ist dran
                aktueller_spieler = "O"
            # Falls die KI dran ist
            elif aktueller_spieler == "O":
                print("Die KI ist am Denken...")

                # Grafik wird mit Graphviz erstellt und später als PNG gespeichert
                self.dot = graphviz.Digraph(comment='TicTacToe-Minimax-Tree', format='png')
                self.besuchte_knoten = set() # Werden gespeichert um Knoten nicht doppelt zu drawen
                wurzel_id = self.zeichne_knoten(spielfeld, 0) # Wurzel entspricht dem Zustand bevor die KI sich entscheidet

                # Alle möglichen Züge werden berechnet
                moegliche_zuege = self.berechne_moegliche_zuege(spielfeld, aktueller_spieler)

                # Simpler Minimax-Algorithmus
                bester_wert = float('-inf')
                bester_zustand = 0
                wenigste_schritte = float('inf')
                for neuer_zustand in moegliche_zuege:
                    # Nur wenn hier eine parent_id angegeben wird, werden die Zustände visualisiert
                    wert, anzahl_schritte = self.minimax(neuer_zustand, False, 1, wurzel_id, self.max_visuelle_tiefe) # Weil die KI schon in dieser Schleife dran ist, wird beim ersten Aufruf von Minimax das Minimum gesucht
                    # Falls ein besseres Resultat oder das gleiche Resultat aber schneller erzeugt wird
                    if wert > bester_wert or (wert == bester_wert and anzahl_schritte < wenigste_schritte):
                        bester_wert = wert
                        bester_zustand = neuer_zustand
                        wenigste_schritte = anzahl_schritte
                
                # Graphik wird nun gerendert, als png gespeichert und mit matplotlib visuell dargestellt
                self.zug_nr += 1 # Zur Benennung der Pngs
                png_path = f'graphics/minimax_tree_step_{self.zug_nr}' # Speicherpfad
                self.dot.render(png_path, format='png', view=False)
                self.show_png_with_matplotlib(png_path)

                # Der beste nächste Zustand für die KI wird zum Spielfeld
                spielfeld = copy.deepcopy(bester_zustand)
                aktueller_spieler = "X"


            # Prüfen ob einer gewonnen hat
            gewinner = self.pruefe_gewinner(spielfeld)
            if gewinner:
                self.spielfeld_ausgeben(spielfeld)
                print(f"Spieler {gewinner} hat gewonnen!")
                break
            
            # Prüfen ob es ein unentschieden ist
            if self.pruefe_unentschieden(spielfeld):
                self.spielfeld_ausgeben(spielfeld)
                print("Das Spiel endet unentschieden!")
                break

    # Spielfeld wird zu String umgewandelt
    def spielfeld_to_string(self, spielfeld):
        return ''.join(cell if cell != " " else "_" for row in spielfeld for cell in row)

    # Spielfeld wird geprintet
    def spielfeld_ausgeben(self, spielfeld):
        for i, reihe in enumerate(spielfeld):
            print(" | ".join(reihe))
            if i < 2:
                print("-" * 9)

    # Gewinner wird überprüft
    def pruefe_gewinner(self, spielfeld):
        for i in range(3):
            if spielfeld[i][0] == spielfeld[i][1] == spielfeld[i][2] != " ":
                return spielfeld[i][0]
            if spielfeld[0][i] == spielfeld[1][i] == spielfeld[2][i] != " ":
                return spielfeld[0][i]
        
        if spielfeld[0][0] == spielfeld[1][1] == spielfeld[2][2] != " ":
            return spielfeld[0][0]
        if spielfeld[0][2] == spielfeld[1][1] == spielfeld[2][0] != " ":
            return spielfeld[0][2]
        
        return None

    def pruefe_unentschieden(self, spielfeld):
        # Wenn kein einziges Feld frei ist, heißt das, es gibt ein unentschieden
        for reihe in spielfeld:
            if " " in reihe:
                return False
        return True

    def berechne_moegliche_zuege(self, spielfeld, spieler):
        moegliche_zuege = [] # 3D-Array

        # Loop durch jedes Element durch
        for i, reihe in enumerate(spielfeld):
            for j, element in enumerate(reihe):
                if element == " ":
                    # Wir erstellen eine Kopie vom Spielfeld und setzen dann abhängig von i und j das Zeichen des Spielers
                    neues_spielfeld = copy.deepcopy(spielfeld)  # Deepcopy, weil sonst 3x3-Struktur nicht mitkopiert wird
                    neues_spielfeld[i][j] = spieler  # Spieler setzt sein Zeichen
                    moegliche_zuege.append(neues_spielfeld) # Zustand wird zur Liste hinzugefügt

        return moegliche_zuege
    
    def bewerte_zustand(self, spielfeld, spieler):
        # Wenn der Spieler gewinnt, wird der Zustand mit 10 bewertet, wenn der Gegner gewinnt mit -10, bei unentschieden mit 0
        gewinner = self.pruefe_gewinner(spielfeld)
        if gewinner == spieler: 
            return 10
        elif gewinner != None:
            return -10
        else:
            return 0

    # KI ist immer "O"
    def minimax(self, spielfeld, istMax, tiefe, parent_id, max_visuelle_tiefe):
        # Visuelle Ergebnisse gibt es nur, wenn eine parent_id angegeben wird
        
        # Falls eine Parent-Id gegeben wurde und die max_visuelle_tiefe noch nicht überschrieben wurde, drawe den Knoten
        if parent_id is not None and tiefe < max_visuelle_tiefe + 1:
            # Zeichne den jetztigen Knoten und erstelle eine Verbindung zum Parent
            node_id = self.zeichne_knoten(spielfeld, tiefe)
            self.zeichne_kante(parent_id, node_id)
        else:
            node_id = None
        
        # Prüfen ob Spiel zu Ende ist
        if self.pruefe_gewinner(spielfeld) != None or self.pruefe_unentschieden(spielfeld) == True:
            return self.bewerte_zustand(spielfeld, "O"), tiefe
        
        # Minimax-Algorithmus
        bester_wert = float('-inf') if istMax else float('inf')
        wenigste_schritte = float('inf')
        moegliche_zuege = self.berechne_moegliche_zuege(spielfeld, "O" if istMax else "X")

        for neuer_zustand in moegliche_zuege:
            # Falls parent_id angegeben wurde, wird dieser Knoten zum nächsten Parent, falls nicht dann wird auch der nächste Knoten nicht visualisiert
            next_parent = node_id if parent_id is not None else None
            wert, anzahl_schritte = self.minimax(neuer_zustand, not istMax, tiefe + 1, next_parent, max_visuelle_tiefe)
            
            # Falls ein besseres Resultat gefunden wird
            if (istMax and wert > bester_wert) or (not istMax and wert < bester_wert):
                bester_wert = wert
                wenigste_schritte = anzahl_schritte
            # Falls das gleich beste Resultat schneller erreicht werden kann
            elif wert == bester_wert and anzahl_schritte < wenigste_schritte:
                wenigste_schritte = anzahl_schritte

        return bester_wert, wenigste_schritte
    
    def show_png_with_matplotlib(self, png_path):
        img = mpimg.imread(png_path + ".png") # Bild wird eingelesen
        plt.figure("TicTacToe-Minimax") # Neues Fenster mit dem Namen wird geöffnet
        plt.clf() # Löscht vorherige Bilder
        plt.imshow(img) # Zeigt das neue Bild
        plt.axis('off') # Versteckt x,z Achsen
        plt.tight_layout()

        # Das Fenster soll automatisch groß sein
        #wm = plt.get_current_fig_manager()
        #wm.window.state('zoomed')

        plt.show(block=False)
        plt.pause(0.1)

    def zeichne_knoten(self, spielfeld, tiefe):
        node_id = f"{self.spielfeld_to_string(spielfeld)}_{tiefe}"
        if node_id not in self.besuchte_knoten:
            label = (
                f"{spielfeld[0][0]} | {spielfeld[0][1]} | {spielfeld[0][2]}\n"
                f"--+---+--\n"
                f"{spielfeld[1][0]} | {spielfeld[1][1]} | {spielfeld[1][2]}\n"
                f"--+---+--\n"
                f"{spielfeld[2][0]} | {spielfeld[2][1]} | {spielfeld[2][2]}"
            )
            farbe = "white"
            gewinner = self.pruefe_gewinner(spielfeld)
            if gewinner == "O":
                farbe = "green"
            elif gewinner == "X":
                farbe = "red"
            elif self.pruefe_unentschieden(spielfeld):
                farbe = "deepskyblue"
            self.dot.node(node_id, label=label, shape="box", style="filled", fillcolor=farbe, fontname="Courier", fontsize="10")
            self.besuchte_knoten.add(node_id)
        return node_id

    def zeichne_kante(self, von, nach):
        self.dot.edge(von, nach)




if __name__ == "__main__":
    ttt = TicTacToe()
    ttt.tic_Tac_toe()