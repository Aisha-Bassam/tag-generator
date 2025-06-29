import xml.etree.ElementTree as ET
import re

# File paths
input_file = "Master Template SVG.svg"
output_file = "Rebuilt Base Template.svg"

# Register SVG namespace
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace('', SVG_NS)

# Parse input SVG
tree = ET.parse(input_file)
root = tree.getroot()

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
