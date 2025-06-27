"""
main.py - Point d'entrée principal du simulateur de parachute guidé.

Ce fichier exécute l'interface principale basée sur Streamlit.
L'utilisateur peut :
    - sélectionner une position géographique,
    - visualiser les champs de vent,
    - lancer la simulation de trajectoire.

:author: Linda Ghazouani, Syrine Boudef, Wilson David Parra Oliveros
:date: 26/06/2026
"""

from streamlit_en_POO import InterfaceStreamlit

def main():
    """
    Lance l'interface utilisateur de simulation via Streamlit.

    Cette fonction :
        - instancie l'objet `InterfaceStreamlit`,
        - appelle la méthode `afficher_interface()` pour démarrer l'affichage interactif.
    """
    app = InterfaceStreamlit()
    app.afficher_interface()

# Exécution uniquement si le fichier est lancé comme script principal
if __name__ == "__main__":
    main()
