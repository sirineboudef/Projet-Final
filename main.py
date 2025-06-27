"""
main.py - Point d'entrée du simulateur de parachute guidé

Ce fichier exécute l'interface principale basée sur Streamlit.
L'utilisateur peut sélectionner une position, visualiser les vents et lancer une simulation.
"""

from streamlit_en_POO import InterfaceStreamlit

def main():
    """
    Lance l'interface Streamlit du simulateur.
    """
    app = InterfaceStreamlit()
    app.afficher_interface()

# Exécution uniquement si le fichier est appelé directement
if __name__ == "__main__":
    main()
