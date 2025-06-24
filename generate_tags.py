import segno
import lxml.etree as ET
import os, io

TEMPLATE_PATH = 'Rebuilt Base Template.svg'
OUTPUT_DIR = 'outputs'
NUMBER = '0058384'
URL = f'https://app.netzero.sa/tag/{NUMBER}'
QR_SIZE_PX = 43.8

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Generate <path> from QR ---
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

# --- Generate number text element ---
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

# --- Prepare modified template with white background ---
def modify_template(template_path: str, number: str) -> ET.ElementTree:
    tree = ET.parse(template_path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Remove red box
    for elem in root.findall(".//svg:rect", namespaces=ns):
        if elem.get("fill") in ("#ff0000", "red"):
            root.remove(elem)

    # Remove number placeholder
    for elem in root.findall(".//svg:text", namespaces=ns):
        if number in ''.join(elem.itertext()).strip():
            root.remove(elem)

    # Add white background rectangle
    bg = ET.Element('{http://www.w3.org/2000/svg}rect', {
        'x': '187.5',
        'y': '229',   # slightly higher to fully cover
        'width': '43.8',
        'height': '55',
        'fill': 'white'
    })
    root.append(bg)

    return tree

# --- Create a single tag file ---
def generate_tag_on_template(template_path, output_path, number, qr_url):
    tree = ET.parse(template_path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Clean template: remove red placeholder
    for elem in root.findall(".//svg:rect", namespaces=ns):
        if elem.get("fill") in ("#ff0000", "red"):
            root.remove(elem)

    # Remove number placeholder
    for elem in root.findall(".//svg:text", namespaces=ns):
        if number in ''.join(elem.itertext()).strip():
            root.remove(elem)

    # Create top-level group that is NOT inside the template's layers
    overlay = ET.Element('{http://www.w3.org/2000/svg}g', {
        'id': 'qr-output-layer',
        'style': 'isolation: isolate;'  # Ensure it's not clipped
    })

    # Add white box
    bg = ET.Element('{http://www.w3.org/2000/svg}rect', {
        'x': '187.5',
        'y': '229',
        'width': '43.8',
        'height': '55',
        'fill': 'white'
    })
    overlay.append(bg)

    # Add QR
    qr_path = generate_qr_path_element(qr_url, fill_color='red')
    if qr_path is not None:
        qr_path.set("transform", "translate(187.5,234.5) scale(1.1838)")
        overlay.append(qr_path)

    # Add number
    number_text = generate_number_text_element(number, x=209.4, y=230, fill_color='red')
    overlay.append(number_text)

    # Add overlay last so it sits on top
    root.append(overlay)

    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    print(f"✅ Saved tag to {output_path}")

# --- Main controller ---
# def main():
    # tree = modify_template(TEMPLATE_PATH, NUMBER)
    # output_path = os.path.join(OUTPUT_DIR, f'tag_{NUMBER}.svg')
    # generate_tag_on_template(tree, NUMBER, URL, output_path)

if __name__ == '__main__':
    output_path = os.path.join(OUTPUT_DIR, f'tag_{NUMBER}.svg')
    generate_tag_on_template('Master Template SVG.svg', output_path, NUMBER, URL)

