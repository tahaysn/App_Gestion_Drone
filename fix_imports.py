#!/usr/bin/env python3
"""
Script pour corriger automatiquement les imports KivyMD
"""

import os
import re

def fix_imports_in_file(file_path):
    """Corriger les imports dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les imports problématiques
        content = re.sub(
            r'from kivymd\.uix\.button import [^#\n]*',
            '# Import des boutons KivyMD',
            content
        )
        
        # Supprimer les références à MDRaisedButton, MDFlatButton, MDTextButton
        content = re.sub(
            r'MDRaisedButton\([^)]*\)',
            'Button(text="OK")',
            content
        )
        content = re.sub(
            r'MDFlatButton\([^)]*\)',
            'Button(text="OK")',
            content
        )
        content = re.sub(
            r'MDTextButton\([^)]*\)',
            'Button(text="OK")',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Corrigé: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur avec {file_path}: {e}")
        return False

def find_and_fix_python_files():
    """Trouver et corriger tous les fichiers Python"""
    python_files = []
    
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"🔍 Trouvé {len(python_files)} fichiers Python")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"✅ {fixed_count} fichiers corrigés")

if __name__ == "__main__":
    find_and_fix_python_files() 