import xml.etree.ElementTree as ET
import re

# File paths
input_file = "Master Template SVG.svg"
output_file = "Rebuilt Base Template.svg"

# Register SVG namespace
ET.register_namespace('', "http://www.w3.org/2000/svg")

# Parse input SVG
tree = ET.parse(input_file)
root = tree.getroot()

# Create new SVG root with same attributes
new_svg = ET.Element(root.tag, root.attrib)

# Copy <defs> block directly if present
for child in root:
    if child.tag.endswith('defs'):
        new_svg.append(child)

# Check if an element is visually relevant (except number text)
def is_visual(elem):
    tag = elem.tag.lower()
    if tag.endswith('text'):
        text = ''.join(elem.itertext()).strip()
        return not re.fullmatch(r'\d{7}', text)  # remove 7-digit numbers
    return True  # keep all other elements like <g>, <use>, <path>, <image>

# Recursive visual copy
def copy_visuals(src_elem, dest_elem):
    for child in src_elem:
        if is_visual(child):
            new_child = ET.Element(child.tag, child.attrib)
            if child.text:
                new_child.text = child.text
            if child.tail:
                new_child.tail = child.tail
            copy_visuals(child, new_child)
            dest_elem.append(new_child)

copy_visuals(root, new_svg)


# Save new SVG
ET.ElementTree(new_svg).write(output_file, encoding="utf-8", xml_declaration=True)
print(f"Rebuilt template saved to {output_file}")
