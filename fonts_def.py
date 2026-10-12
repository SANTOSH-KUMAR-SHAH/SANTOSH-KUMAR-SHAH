import os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "fonts_embedded.css"), "r", encoding="utf-8") as f:
    RAW_FONTS_CSS = f.read()

# Ready to drop into SVG <style> tags (escaped for Python f-strings)
FONTS_STYLE_ESCAPED = RAW_FONTS_CSS.replace("{", "{{").replace("}", "}}")
