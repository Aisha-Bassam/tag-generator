import xml.etree.ElementTree as ET
import re

# File paths
input_file = "Master Template SVG.svg"
output_file = "Rebuilt Base Template.svg"

# # Register SVG namespace
# SVG_NS = "http://www.w3.org/2000/svg"
# ET.register_namespace('', SVG_NS)

# Register SVG namespace
SVG_NS = "http://www.w3.org/2000/svg"
AI_NS = "http://ns.adobe.com/AdobeIllustrator/10.0/"
ET.register_namespace('', SVG_NS)
ET.register_namespace('i', AI_NS)  # force Illustrator-compatible prefix

# Parse input SVG
tree = ET.parse(input_file)
root = tree.getroot()
# root.attrib['width'] = '7cm'
# root.attrib['height'] = '2.5cm'
# root.attrib['scale'] = '0.1'
# root.attrib['viewBox'] = '0 0 264.6 94.5'  # 7cm × 2.5cm at 37.8 px/cm


# === STEP 1: Remove any <text> that is exactly a 7-digit number ===
for parent in root.iter():
    children = list(parent)  # clone child list to avoid iterator issues
    for child in children:
        if child.tag == f'{{{SVG_NS}}}text':
            text_content = ''.join(child.itertext()).strip()
            if re.fullmatch(r'\d{7}', text_content):
                parent.remove(child)


# === STEP 2: Write output file ===
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"✅ Rebuilt template saved to: {output_file}")
