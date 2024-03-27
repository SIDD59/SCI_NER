import os
import io
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
import fitz
import spacy
from collections import defaultdict
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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

def process_pdf(input_file, output_file, accuracy_ratio):
    # Open the PDF
    pdfDoc = fitz.open(input_file)
    total_matches = 0
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
    
    # Add entity_label as additional key
    formatted_data1 = []
    for (entity_label, entity_text), entity_data in entity_data_dict.items():
        formatted_data1.append({
            'entity_label': entity_label,
            'entity_data': entity_data['entity_data']
        })

    # Group data by entity_label
    formatted_data2 = {}
    for item in formatted_data1:
        label = item['entity_label']
        data = item['entity_data']
        if label not in formatted_data2:
            formatted_data2[label] = []
        formatted_data2[label].extend(data)

    
    # Combine page numbers for each entity_label and entity_data pair
    formatted_data3 = []
    for label, data in formatted_data2.items():
        entity_text_page_map = {}
        for text, page in data:
            if text not in entity_text_page_map:
                entity_text_page_map[text] = []
            entity_text_page_map[text].append(page)
    
        formatted_entity_data = [[text, sorted(list((set(pages))))] for text, pages in entity_text_page_map.items()]
        formatted_data3.append({'entity_label': label, 'entity_data': formatted_entity_data})

    formatted_data4 = []
    for item in formatted_data3:
        formatted_data4.append({'entity_label': item['entity_label'], 'entity_data': combine_similar_entities(item['entity_data'], accuracy_ratio)})
   
    # Save the output PDF
    #pdfDoc.save(output_file)
    pdfDoc.close()
    return formatted_data4

#Combine similar entities and their page number susing fuzzy ratio method
def combine_similar_entities(entities, accuracy_ratio):
    combined_entities = []
    for entity in entities:
        found = False
        for combined_entity in combined_entities:
            for existing_entity in combined_entity:
                ratio = fuzz.ratio(entity[0].lower().strip(), existing_entity[0].lower().strip())
                if ratio > accuracy_ratio :
                    existing_entity[1].extend(entity[1])
                    found = True
                    break
            if found:
                break
        if not found:
            combined_entities.append([entity])
    return combined_entities

def convert_and_highlight_pdf(uploaded_file_path, processed_path, output_path, accuracy_ratio):
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

    # Process the processed PDF to highlight and combine named entities
    final_formatted_data = process_pdf(processed_path, output_path, accuracy_ratio)

    os.remove(processed_path)
    print(final_formatted_data)
    return  final_formatted_data
