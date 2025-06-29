import lxml.etree as ET
import os, io
from qrcodegen import QrCode
import zipfile
from tqdm import tqdm  # Optional: for a progress bar

START = 58384
# END = 114383
END = 58484
# BATCH_SIZE = 1000
BATCH_SIZE = 10

TEMPLATE_PATH = 'Rebuilt Base Template.svg'
OUTPUT_DIR = 'outputs'
NUMBER = '0058384'
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

def pad_number(num):
    return str(num).zfill(7)

def generate_batch_zip(start, end):
    batch_folder = os.path.join(OUTPUT_DIR, f"temp_{start}-{end}")
    os.makedirs(batch_folder, exist_ok=True)

    for n in tqdm(range(start, end + 1), desc=f"Generating {start}-{end}"):
        num_str = pad_number(n)
        url = f"https://app.netzero.sa/tag/{num_str}"
        output_path = os.path.join(batch_folder, f'tag_{num_str}.svg')
        generate_tag_on_template(TEMPLATE_PATH, output_path, num_str, url)

    zip_name = os.path.join(OUTPUT_DIR, f"{pad_number(start)}-{pad_number(end)}.zip")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(batch_folder):
            zipf.write(os.path.join(batch_folder, file), file)
    print(f"📦 Created ZIP: {zip_name}")

    # Clean up
    for f in os.listdir(batch_folder):
        os.remove(os.path.join(batch_folder, f))
    os.rmdir(batch_folder)

# if __name__ == '__main__':
#     output_path = os.path.join(OUTPUT_DIR, f'tag_{NUMBER}.svg')
#     generate_tag_on_template(TEMPLATE_PATH, output_path, NUMBER, URL)

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for batch_start in range(START, END + 1, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE - 1, END)
        generate_batch_zip(batch_start, batch_end)
