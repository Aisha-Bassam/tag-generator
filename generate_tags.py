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
# def generate_qr_path_element(url: str, fill_color: str = 'white'):
#     qr = segno.make(url)
#     buffer = io.BytesIO()

#     qr.save(buffer, kind='svg', xmldecl=False, scale=10, omitsize=True)
#     buffer.seek(0)
#     svg_string = buffer.read().decode('utf-8')
#     root = ET.fromstring(svg_string)
    
#     for elem in root.iter():
#         if ET.QName(elem).localname == 'path':
#             elem.set('fill', fill_color)
#             # elem.set('stroke', 'red')
#             # elem.set('stroke-width', '0.1')
#             return elem
#     return None

def generate_qr_path_element(url: str, fill_color: str = 'white'):
    qr = segno.make(url)
    buffer = io.BytesIO()

    qr.save(buffer, kind='svg', xmldecl=False, scale=10, omitsize=True)
    buffer.seek(0)
    svg_string = buffer.read().decode('utf-8')
    root = ET.fromstring(svg_string)

    # Create a group element to hold all QR paths
    group = ET.Element('{http://www.w3.org/2000/svg}g')

    # Collect and insert all path elements
    for elem in root.iter():
        if ET.QName(elem).localname == 'path':
            elem.set('fill', fill_color)
            elem.set('stroke', 'red')
            elem.set('stroke-width', '0.1')
            group.append(elem)

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



    # Generate QR path
    qr_path = generate_qr_path_element(qr_url, fill_color='white')
    if qr_path is not None:
        scale_factor = width / (37 * 10)
        qr_path.set("transform", f"translate({x},{y}) scale({scale_factor})")

        # Insert the QR path in place of the placeholder
        parent = placeholder.getparent()
        index = list(parent).index(placeholder)
        parent.remove(placeholder)
        parent.insert(index, qr_path)

    # Add number text matching original style and placement
    transform = "translate(28.9 111.19)"
    number_text = generate_number_text_element(number, transform=transform, fill_color='white')
    root.append(number_text)

    # Write output file
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    print(f"✅ Saved tag to {output_path}")


if __name__ == '__main__':
    output_path = os.path.join(OUTPUT_DIR, f'tag_{NUMBER}.svg')
    generate_tag_on_template(TEMPLATE_PATH, output_path, NUMBER, URL)
