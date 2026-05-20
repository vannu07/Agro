import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def docx_to_text(docx_path, output_path):
    print(f"Opening {docx_path}...")
    try:
        with zipfile.ZipFile(docx_path) as z:
            print("Zip opened successfully.")
            xml_content = z.read('word/document.xml')
            print("word/document.xml read successfully.")
        
        tree = ET.fromstring(xml_content)
        text = []
        
        # Word XML namespaces
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        print("Extracting text blocks...")
        for p in tree.findall('.//w:p', ns):
            p_text = []
            for r in p.findall('.//w:r', ns):
                for t in r.findall('.//w:t', ns):
                    if t.text:
                        p_text.append(t.text)
            text.append(''.join(p_text))
            
        final_text = '\n'.join(text)
        print(f"Extracted {len(final_text)} characters.")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_text)
        print(f"Text written to {output_path}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        docx_path = sys.argv[1]
        output_path = sys.argv[2]
        if docx_to_text(docx_path, output_path):
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("Usage: python extract_docx.py <path_to_docx> <output_path>")
        sys.exit(1)
