# Configuration file for the Sphinx documentation builder.
import os
import sys
from datetime import datetime

# --- Путь к корню проекта (от docs/source до корня) ---
# docs/source/conf.py → ../.. → корень проекта
sys.path.insert(0, os.path.abspath('../..'))

# --- Project information ---
project = 'Weather App'
copyright = f'{datetime.now().year}, Maxim'
author = 'Maxim'
release = '1.0.0'

# --- General configuration ---
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',  # Добавлено!
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'ru'

# --- HTML output ---
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# --- Автодокументация ---
autosummary_generate = True  # Генерировать .rst для модулей
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '__init__',
    'inherited-members': True,
    'show-inheritance': True,
}