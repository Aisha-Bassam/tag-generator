import segno
import lxml.etree as ET
import os, io

TEMPLATE_PATH = 'Master Template SVG.svg'
OUTPUT_DIR = 'outputs'
NUMBER = '0058384'
URL = f'https://app.netzero.sa/tag/{NUMBER}'
QR_SIZE_PX = 43.8  # width and height

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_qr_svg_data(url):
    qr = segno.make(url)
    buffer = io.BytesIO()
    qr.save(buffer, kind='svg', xmldecl=False)  # <--- This disables the XML declaration
    buffer.seek(0)
    return buffer.read().decode('utf-8')


def main():
    # Load SVG template
    tree = ET.parse(TEMPLATE_PATH)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Remove red box (identified by color or ID)
    for elem in root.findall(".//svg:rect", namespaces=ns):
        if elem.get("fill") in ("#ff0000", "red"):
            root.remove(elem)

    # Insert QR Code
    qr_svg = ET.fromstring(generate_qr_svg_data(URL))

    # Create a group to hold the QR code
    g = ET.Element('{http://www.w3.org/2000/svg}g')
    g.append(qr_svg)

    # Move the QR code group to correct position
    g.set("transform", "translate(100, 100) scale(0.2)")  # TEMPORARY placeholder
    root.append(g)

    # Add the number as text
    text = ET.Element('{http://www.w3.org/2000/svg}text', {
        'x': '100',  # TEMPORARY position
        'y': '95',
        'font-family': 'Myriad Pro',
        'font-size': '10',
        'text-anchor': 'middle',
        'fill': 'black'
    })
    text.text = NUMBER
    root.append(text)

    # Save output
    output_path = os.path.join(OUTPUT_DIR, f'tag_{NUMBER}.svg')
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    print(f"Saved {output_path}")

if __name__ == '__main__':
    main()
