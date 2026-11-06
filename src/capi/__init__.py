"""CAPI : planning poker en console.

Le package est séparé en deux couches :
- ``backlog`` et ``game`` : logique pure (aucun print, aucun input), testable sans interface ;
- ``cli`` : interface console, qui ne contient aucune règle de jeu.
"""
