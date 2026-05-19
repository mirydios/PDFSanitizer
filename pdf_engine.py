import pdfplumber
import os
from sanitizer import LGPDSanitizer

class PDFEngine:
    def __init__(self):
        self.sanitizer = LGPDSanitizer()

    def process_pdf(self, file_path_or_stream) -> dict:
        """
        Parses a PDF file from a path or an in-memory stream,
        extracts text and tables, and returns the sanitized outcomes,
        metadata, audit trail, and sanitization statistics.
        """
        metadata = {}
        original_pages_text = []
        sanitized_pages_text = []
        all_tables = []
        full_audit_trail = []
        
        stats = {
            "total_pages": 0,
            "total_masked_items": 0,
            "masked_by_type": {
                "CPF": 0,
                "CNPJ": 0,
                "E-mail": 0,
                "Telefone": 0,
                "Dados Bancários": 0
            }
        }

        # Open the PDF using pdfplumber
        with pdfplumber.open(file_path_or_stream) as pdf:
            # Extract PDF Metadata
            if pdf.metadata:
                metadata = {
                    "title": pdf.metadata.get("Title", "Sem Título"),
                    "author": pdf.metadata.get("Author", "Desconhecido"),
                    "creator": pdf.metadata.get("Creator", "Desconhecido"),
                    "producer": pdf.metadata.get("Producer", "Desconhecido"),
                    "creation_date": pdf.metadata.get("CreationDate", "Desconhecido"),
                    "page_count": len(pdf.pages),
                    "file_size_bytes": getattr(file_path_or_stream, "size", 0) or (os.path.getsize(file_path_or_stream) if isinstance(file_path_or_stream, str) else 0)
                }
            else:
                metadata = {
                    "title": "Sem Título",
                    "author": "Desconhecido",
                    "page_count": len(pdf.pages),
                    "file_size_bytes": getattr(file_path_or_stream, "size", 0) or (os.path.getsize(file_path_or_stream) if isinstance(file_path_or_stream, str) else 0)
                }

            stats["total_pages"] = len(pdf.pages)

            # Process Page by Page
            for i, page in enumerate(pdf.pages):
                page_num = i + 1
                
                # 1. TEXT EXTRACTION
                raw_text = page.extract_text()
                if not raw_text:
                    raw_text = ""
                
                # Sanitize the extracted page text
                masked_text, page_audit = self.sanitizer.sanitize_text(raw_text, page_num=page_num)
                
                original_pages_text.append(raw_text)
                sanitized_pages_text.append(masked_text)
                full_audit_trail.extend(page_audit)

                # Update stats with text counts
                for item in page_audit:
                    item_type = item["type"]
                    if item_type in stats["masked_by_type"]:
                        stats["masked_by_type"][item_type] += 1
                        stats["total_masked_items"] += 1

                # 2. TABLE EXTRACTION
                # pdfplumber table extraction works incredibly well out of the box
                try:
                    extracted_tables = page.extract_tables()
                    for t_idx, table in enumerate(extracted_tables):
                        # Clean cells (replace None with empty string, strip whitespace)
                        cleaned_table = []
                        for row in table:
                            cleaned_row = []
                            for cell in row:
                                if cell is None:
                                    cleaned_row.append("")
                                else:
                                    cleaned_row.append(str(cell).strip())
                            cleaned_table.append(cleaned_row)

                        # Skip completely empty tables
                        if not cleaned_table or all(all(cell == "" for cell in row) for row in cleaned_table):
                            continue

                        # Sanitize table
                        sanitized_table = self.sanitizer.sanitize_table(cleaned_table)

                        all_tables.append({
                            "page": page_num,
                            "table_index": len(all_tables),
                            "original": cleaned_table,
                            "sanitized": sanitized_table
                        })
                except Exception as e:
                    # In case page table structure extraction fails, gracefully proceed
                    print(f"Erro ao extrair tabelas da página {page_num}: {e}")

        # Combine all pages for final presentation
        # (We also send individual pages to make pagination/navigation easier in the frontend)
        combined_original_text = "\n\n--- PÁGINA {} ---\n\n".join(
            original_pages_text[i] for i in range(len(original_pages_text))
        )
        combined_sanitized_text = "\n\n--- PÁGINA {} ---\n\n".join(
            sanitized_pages_text[i] for i in range(len(sanitized_pages_text))
        )

        # Structure final return format
        return {
            "metadata": metadata,
            "original_pages": original_pages_text,
            "sanitized_pages": sanitized_pages_text,
            "original_text_full": combined_original_text,
            "sanitized_text_full": combined_sanitized_text,
            "tables": all_tables,
            "audit_trail": full_audit_trail,
            "stats": stats
        }
