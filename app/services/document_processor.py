import os
from docling.document_converter import DocumentConverter
from config import settings

def convert_html_to_markdown(base_html_docs_path: str, output_base_path: str):
    space_keys = [
        "EMS", "OMS", "OPA", "PMS", "POS", "WSS", "Hstays", "WIKI",
        "CMSupE", "CMSup", "hpn", "pneng", "pnsup", "CRS", "CST",
        "CM", "CME", "HE", "HEYC", "ags", "API", "PDOC", "PDP", "MAN"
    ]


    for past in space_keys:
        html_folder = os.path.join(base_html_docs_path, past)
        if not os.path.exists(html_folder):
            continue

        output_folder = os.path.join(output_base_path, past)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        converter = DocumentConverter()

        for filename in os.listdir(html_folder):
            if not filename.endswith(".html"):
                continue

            output_filename = filename.replace(".html", ".md")
            output_path = os.path.join(output_folder, output_filename)

            filepath = os.path.join(html_folder, filename)
            try:
                result = converter.convert(filepath)
                markdown_content = result.document.export_to_markdown()

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
            except Exception as e:
                continue