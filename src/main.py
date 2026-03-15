# main.py
"""
Data transformation tool for CASA
author: Adrian Velasquez
email: a.velasquezs@uniandes.edu.co
"""

from ui import gui as gui

def main():
    print(
        '\n=== Application started ===\n'
        '\n>> Starting GUI...'
    )
    gui.run()

if __name__ == '__main__':
    main()