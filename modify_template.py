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

# Find the barcode placeholder <rect> by ID and extract its dimensions
barcode_box = None
for elem in root.iter():
    if elem.tag.endswith('rect') and elem.attrib.get('id') == 'barcode-placeholder':
        barcode_box = elem
        break

# If found, insert a white rectangle at the same location
if barcode_box is not None:
    bg = ET.Element('{http://www.w3.org/2000/svg}rect', {
        'x': barcode_box.attrib.get('x', '0'),
        'y': barcode_box.attrib.get('y', '0'),
        'width': barcode_box.attrib.get('width', '0'),
        'height': barcode_box.attrib.get('height', '0'),
        'fill': 'white'
    })

    # Try to insert into the same <g> group with 7 children
    target_group = None
    for elem in new_svg.iter():
        if elem.tag.endswith('g') and len(list(elem)) == 7:
            target_group = elem
            break

    if target_group is not None:
        target_group.insert(0, bg)
    else:
        new_svg.append(bg)

# Save new SVG
ET.ElementTree(new_svg).write(output_file, encoding="utf-8", xml_declaration=True)
print(f"Rebuilt template saved to {output_file}")
