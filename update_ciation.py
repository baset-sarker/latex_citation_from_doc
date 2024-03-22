from docx import Document
import re
# Load the BibTeX file
import bibtexparser
import argparse

def parse_range_make_continuous(s_list: list):
    result = []
    for part in s_list:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start, end + 1))
        else:
            if part != '' and part != " ":
                result.append(int(part))
    return result

def extract_citation_groups(text: str):
    #pattern = r'\[(.*?)\]'  # Pattern to match anything inside square brackets
    pattern = r'\[([\d,-]+)\]' 
    matches = re.findall(pattern, text)
    citation_groups = []
    citation_groups_str = []
    
    for match in matches:
        citation_groups_str.append('['+match+']')
        citations = match.split(',')
        citations = [c.strip() for c in citations]  # Remove leading/trailing spaces
        citation_groups.append(citations)
        
    return citation_groups,citation_groups_str

def extract_references(docx_file):
    doc = Document(docx_file)
    references_section_found = False
    references = []

    for paragraph in doc.paragraphs:
        if "Reference" in paragraph.text:
            references_section_found = True
        elif references_section_found:
            if paragraph.text.strip():  # Check if paragraph is not empty
                references.append(paragraph.text)

    return references

def update_citations(template_file, bib_database, references):
    with open(template_file, 'r') as f:
        template_content = f.read()

   # template_content = "Your content with citation patterns here [1,3-5,7-9,11] if there is [4,3]"

    # extract the citation groups from the template content
    citation_groups,citation_groups_str = extract_citation_groups(template_content)



    for citation,org_text in zip(citation_groups,citation_groups_str):
        cit_strings = ''
        get_digits = parse_range_make_continuous(citation)
        for digit in get_digits:
            reference = references[int(digit)-1]
            print(digit,reference)
        
            for entry in bib_database.entries:
                title = entry['title']
                if title in reference:
                    id = entry['ID']
                    cit_strings += f'\cite{{{id}}}, '

    
        template_content = template_content.replace(f'{org_text}', f'{cit_strings}')
    print(template_content)
    return template_content


# take bib file , template fil ean docx file as arguments

# Create the parser
parser = argparse.ArgumentParser(description='Update citations in the template file')
# Add the arguments
parser.add_argument('bibtex_file', default='references.bib',nargs="?" ,help='Path to the BibTeX file')
parser.add_argument('template_file',default='template.tex',nargs="?", help='Path to the template file')
parser.add_argument('docx_file', default="MP_paper_12 tmh.docx",nargs="?", help='Path to the DOCX file')

# Parse the arguments
args = parser.parse_args()

# Read the BibTeX file
with open(args.bibtex_file) as bib_file:
    bib_database = bibtexparser.load(bib_file)

# Extract references from the DOCX file
references = extract_references(args.docx_file)

# Update citations in the template file
updated_template_content = update_citations(args.template_file, bib_database, references)

# Write updated content back to the template file
with open("new_template.tex", 'w') as f:
    f.write(updated_template_content)

print("Citations in the template file have been updated.")