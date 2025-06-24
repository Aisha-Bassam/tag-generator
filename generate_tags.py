import segno
import lxml.etree as ET
import os, io

TEMPLATE_PATH = 'Master Template SVG.svg'
OUTPUT_DIR = 'outputs'
NUMBER = '0058384'
URL = f'https://app.netzero.sa/tag/{NUMBER}'
QR_SIZE_PX = 43.8  # Target size

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Function to generate a red QR path ---
def generate_qr_path_element(url: str, fill_color: str = 'red'):
    qr = segno.make(url)
    buffer = io.BytesIO()
    qr.save(buffer, kind='svg', xmldecl=False, scale=1, omitsize=True)
    buffer.seek(0)
    svg_string = buffer.read().decode('utf-8')
    root = ET.fromstring(svg_string)

    for elem in root.iter():
        if elem.tag.endswith('path'):
            elem.set('fill', fill_color)
            return elem
    return None

# --- Function to create the number text element ---
def generate_number_text_element(number: str, x: float, y: float, font_size: int = 10, fill_color: str = 'red'):
    text = ET.Element('{http://www.w3.org/2000/svg}text', {
        'x': str(x),
        'y': str(y),
        'font-family': 'Myriad Pro',
        'font-size': str(font_size),
        'text-anchor': 'middle',
        'fill': fill_color
    })
    text.text = number
    return text

# --- Function to create a complete tag from template ---
def create_tag_svg(template_path, output_path, number, qr_url):
    tree = ET.parse(template_path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Remove red square
    for elem in root.findall(".//svg:rect", namespaces=ns):
        if elem.get("fill") in ("#ff0000", "red"):
            root.remove(elem)

    # Remove existing number text
    for elem in root.findall(".//svg:text", namespaces=ns):
        if number in ''.join(elem.itertext()).strip():
            root.remove(elem)

    # --- Insert QR code ---
    qr_path = generate_qr_path_element(qr_url)
    if qr_path is not None:
        qr_path.set("transform", "translate(187.5, 234.5) scale(1.1838)")
        root.insert(0, qr_path)

    # --- Insert number ---
    number_text = generate_number_text_element(number, x=209.4, y=230)
    root.insert(0, number_text)

    # --- Save ---
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    print(f"✅ Saved {output_path}")

# --- Run a single test ---
if __name__ == '__main__':
    output_path = os.path.join(OUTPUT_DIR, f'tag_{NUMBER}.svg')
    create_tag_svg(TEMPLATE_PATH, output_path, NUMBER, URL)
