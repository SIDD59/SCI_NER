import os
import io
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
import fitz
import spacy
from collections import defaultdict
import json

CONTENT_PATH = os.environ["CONTENT_PATH"]

nlp = spacy.load("en_legal_ner_trf")

def highlight_entities(page):
    """
    Highlight named entities in the page
    """
    matches_found = 0

    doc = nlp(page.get_text("text"))

    for ent in doc.ents:
        entity_type = ent.label_
        matching_val_area = page.search_for(ent.text)
        if entity_type == "COURT":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (1, 0, 0), "fill": (1, 0, 0, 0.1)})
            highlight.update()
            matches_found += 1
        elif entity_type == "PETITIONER":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0, 1, 0), "fill": (0, 1, 0, 0.1)})
            highlight.update()
            matches_found += 1
        elif entity_type == "RESPONDENT":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0.2549, 0.4118, 0.8824), "fill":  (0.1, 0.3, 0.8)})
            highlight.update()
            matches_found += 1
        elif entity_type == "JUDGE":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (1, 1, 0), "fill":  (1, 1, 0, 0.1)})
            highlight.update()
            matches_found += 1
        elif entity_type == "LAWYER":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0.7843, 0.6275, 1.0), "fill":  (0.7843, 0.6275, 1.0, 0.1)})
            highlight.update()
            matches_found += 1
        elif entity_type == "DATE":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (1, 0.647, 0), "fill":  (1, 0.647, 0, 0.1)})
            highlight.update()
            matches_found += 1 
        elif entity_type == "ORG":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0, 1, 1), "fill":  (0, 1, 1, 0.1)})
            highlight.update()
            matches_found += 1
        elif entity_type == "GPE":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (1, 0, 1), "fill":  (1, 0, 1, 0.1)})
            highlight.update()
            matches_found += 1
        elif entity_type == "STATUTE":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (1, 0.753, 0.796), "fill":  (1, 0.753, 0.796, 0.1)})
            highlight.update()
            matches_found += 1 
        elif entity_type == "PROVISION":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0.749, 1, 0), "fill":  (0.749, 1, 0, 0.1)})
            highlight.update()
            matches_found += 1 
        elif entity_type == "PRECEDENT":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0, 0.5, 0.5), "fill":  (0, 0.5, 0.5, 0.1)})
            highlight.update()
            matches_found += 1
        elif entity_type == "CASE_NUMBER":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0.647, 0.165, 0.165), "fill":  (0.647, 0.165, 0.165, 0.1)})
            highlight.update()
            matches_found += 1
        elif entity_type == "WITNESS":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0.529, 0.808, 0.922), "fill":  (0.529, 0.808, 0.922, 0.1)})
            highlight.update()
            matches_found += 1  
        elif entity_type == "OTHER_PERSON":
            highlight = page.add_highlight_annot(matching_val_area)
            highlight.set_colors({"stroke": (0.5, 0.5, 0.5), "fill":  (0.5, 0.5, 0.5, 0.1)})
            highlight.update()
            matches_found += 1   
    return matches_found

def process_pdf(input_file, output_file):
    # Open the PDF
    pdfDoc = fitz.open(input_file)
    #total_matches = 0
    print(f"page count: {pdfDoc.page_count}")

    # Initialize a dictionary to store the counts of matches for each entity type
    total_matches_counts = defaultdict(int)
    entity_data_dict = defaultdict(lambda: {'entity_data': []})

    # Iterate through pages
    for pg in range(pdfDoc.page_count):
        page = pdfDoc[pg]
        #matches_found = highlight_entities(page)
        #total_matches += matches_found

        doc = nlp(page.get_text("text"))

        for ent in doc.ents:
            entity_label = ent.label_
            entity_text = ent.text

            # Add the page number to the list for the entity
            entity_data_dict[(entity_label, entity_text)]['entity_data'].append([entity_text, pg+1])
    
    formatted_data = []
    for (entity_label, entity_text), entity_data in entity_data_dict.items():
        formatted_data.append({
            'entity_label': entity_label,
            'entity_data': entity_data['entity_data']
        })

    # Group data by entity_label
    grouped_data = {}
    for item in formatted_data:
        label = item['entity_label']
        data = item['entity_data']
        if label not in grouped_data:
            grouped_data[label] = []
        grouped_data[label].extend(data)

    # Combine page numbers for each entity_label and entity_data pair
    final_formatted_data = []
    for label, data in grouped_data.items():
        entity_text_page_map = {}
        for text, page in data:
            if text not in entity_text_page_map:
                entity_text_page_map[text] = []
            entity_text_page_map[text].append(page)
    
        formatted_entity_data = [[text, sorted(list((set(pages))))] for text, pages in entity_text_page_map.items()]
        final_formatted_data.append({'entity_label': label, 'entity_data': formatted_entity_data})
   
    # Save the output PDF
    #pdfDoc.save(output_file)
    pdfDoc.close()
    return final_formatted_data

def convert_and_highlight_pdf(uploaded_file_path, processed_path, output_path):
    # Convert PDF to images
    images = convert_from_path(uploaded_file_path)

    pdf_writer = PyPDF2.PdfWriter()

    for image in images:
        # Convert images to PDF using PyTesseract
        page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
        pdf = PyPDF2.PdfReader(io.BytesIO(page))
        pdf_writer.add_page(pdf.pages[0])

    
    # Export the searchable PDF
    with open(processed_path, "wb") as f:
        pdf_writer.write(f)

    # Process the processed PDF to highlight named entities
    final_formatted_data = process_pdf(processed_path, output_path)

    os.remove(processed_path)
    print(final_formatted_data)
    return  final_formatted_data
