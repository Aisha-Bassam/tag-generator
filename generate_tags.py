import lxml.etree as ET
import os, io
from qrcodegen import QrCode

TEMPLATE_PATH = 'Rebuilt Base Template.svg'
OUTPUT_DIR = 'outputs'
NUMBER = '0058385'
URL = f'https://app.netzero.sa/tag/{NUMBER}'
QR_SIZE_PX = 43.8

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Generate QR using qrcodegen ---
def generate_qrcodegen_element(url: str, module_size: float = 1.0, fill_color: str = 'white'):
    qr = QrCode.encode_text(url, QrCode.Ecc.MEDIUM)

    group = ET.Element('{http://www.w3.org/2000/svg}g')

    for y in range(qr.get_size()):
        for x in range(qr.get_size()):
            if qr.get_module(x, y):
                rect = ET.Element('{http://www.w3.org/2000/svg}rect', {
                    'x': str(x * module_size),
                    'y': str(y * module_size),
                    'width': str(module_size),
                    'height': str(module_size),
                    'fill': fill_color
                })
                group.append(rect)

    group.set("shape-rendering", "crispEdges")
    return group

# --- Generate number text element ---
def generate_number_text_element(number: str, transform: str, fill_color: str = 'white'):
    text = ET.Element('{http://www.w3.org/2000/svg}text', {
        'transform': transform,
        'font-family': 'Myriad Pro',
        'font-size': '6.5',
        'text-anchor': 'start',
        'fill': fill_color
    })
    tspan = ET.Element('{http://www.w3.org/2000/svg}tspan', {
        'x': '0',
        'y': '0'
    })
    tspan.text = number
    text.append(tspan)
    return text

# --- Create a single tag file ---
def generate_tag_on_template(template_path, output_path, number, qr_url):
    tree = ET.parse(template_path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Locate the barcode placeholder rect by ID
    placeholder = None
    for elem in root.iter():
        if ET.QName(elem).localname == 'rect' and elem.attrib.get('id') == 'barcode-placeholder':
            placeholder = elem
            break

    if placeholder is None:
        raise ValueError("❌ barcode-placeholder not found in template")

    x = float(placeholder.attrib['x'])
    y = float(placeholder.attrib['y'])
    width = float(placeholder.attrib['width'])
    height = float(placeholder.attrib['height'])

    # Generate QR using qrcodegen
    qr = QrCode.encode_text(qr_url, QrCode.Ecc.MEDIUM)
    qr_group = generate_qrcodegen_element(qr_url, module_size=1.0, fill_color='white')
    qr_size = qr.get_size()
    scale_x = width / qr_size
    scale_y = height / qr_size
    qr_group.set('transform', f'translate({x},{y}) scale({scale_x},{scale_y})')

    # Replace placeholder with QR group
    parent = placeholder.getparent()
    index = list(parent).index(placeholder)
    parent.remove(placeholder)
    parent.insert(index, qr_group)

    # Add number text
    transform = "translate(28.9 111.19)"
    number_text = generate_number_text_element(number, transform=transform, fill_color='white')
    root.append(number_text)

    # Write output file
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    print(f"✅ Saved tag to {output_path}")

if __name__ == '__main__':
    output_path = os.path.join(OUTPUT_DIR, f'tag_{NUMBER}.svg')
    generate_tag_on_template(TEMPLATE_PATH, output_path, NUMBER, URL)
