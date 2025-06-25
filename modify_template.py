import xml.etree.ElementTree as ET
import re
import copy

# File paths
input_file = "Master Template SVG.svg"
output_file = "Rebuilt Base Template.svg"

# Register SVG namespace
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace('', SVG_NS)

# Parse input SVG
tree = ET.parse(input_file)
root = tree.getroot()

# Deep copy to preserve all structure and metadata
new_svg = copy.deepcopy(root)

# === STEP 1: Remove any <text> that is exactly a 7-digit number ===
for parent in new_svg.iter():
    children = list(parent)  # clone child list to avoid iterator issues
    for child in children:
        if child.tag == f'{{{SVG_NS}}}text':
            text_content = ''.join(child.itertext()).strip()
            if re.fullmatch(r'\d{7}', text_content):
                parent.remove(child)

# # === STEP 2: Find the <rect id="barcode-placeholder"> and insert a white box ===
# placeholder_rect = new_svg.find(f".//{{{SVG_NS}}}rect[@id='barcode-placeholder']")
# if placeholder_rect is not None:
#     x = placeholder_rect.attrib.get("x", "0")
#     y = placeholder_rect.attrib.get("y", "0")
#     width = placeholder_rect.attrib.get("width", "40")
#     height = placeholder_rect.attrib.get("height", "40")

#     white_box = ET.Element(f'{{{SVG_NS}}}rect', {
#         "x": x,
#         "y": y,
#         "width": width,
#         "height": height,
#         "fill": "white"
#     })

#     # Insert just after placeholder
#     for parent in new_svg.iter():
#         if placeholder_rect in parent:
#             index = list(parent).index(placeholder_rect)
#             parent.insert(index + 1, white_box)
#             break

# === STEP 3: Write output file ===
ET.ElementTree(new_svg).write(output_file, encoding="utf-8", xml_declaration=True)
print(f"✅ Rebuilt template saved to: {output_file}")
