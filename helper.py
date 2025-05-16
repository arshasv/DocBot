import fitz  # PyMuPDF
import pandas as pd

def extract_project_details(overview_path, estimation_path):
    overview_text = ""
    with fitz.open(overview_path) as doc:
        for page in doc:
            overview_text += page.get_text()

    estimation_data = pd.read_excel(estimation_path)
    return overview_text, estimation_data

def generate_final_document(tasks):
    sections = []
    for task in tasks:
        sections.append(f"## {task.name}\n{task.output}\n")
    with open("output/functional_documentation.md", "w") as f:
        f.writelines(sections)
