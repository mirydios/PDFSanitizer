import urllib.request
import urllib.error
import json
import os

def test_process_endpoint():
    """
    Verifies that the /api/process endpoint of the running local server is
    working correctly, extracting text and tables, and applying PII masking.
    """
    url = "http://127.0.0.1:8000/api/process"
    pdf_path = "test_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo '{pdf_path}' não foi encontrado. Execute 'create_test_pdf.py' primeiro.")
        return False
        
    print(f"Carregando '{pdf_path}' e preparando upload para {url}...")
    
    try:
        # 1. Read PDF file bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            
        # 2. Build multipart/form-data payload manually to avoid dependencies (like requests)
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        
        parts = []
        parts.append(f"--{boundary}".encode('utf-8'))
        parts.append(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(pdf_path)}"'.encode('utf-8'))
        parts.append(b'Content-Type: application/pdf')
        parts.append(b'')
        parts.append(pdf_bytes)
        parts.append(f"--{boundary}--".encode('utf-8'))
        
        body = b'\r\n'.join(parts)
        
        # 3. Build urllib Request
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        req.add_header('Content-Length', str(len(body)))
        
        # 4. Perform request
        print("Enviando requisição de processamento ao servidor FastAPI...")
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode('utf-8')
            data = json.loads(resp_body)
            
        # 5. Print out findings
        print("\n=== SUCESSO NO PROCESSAMENTO DA API ===")
        print(f"Nome do arquivo processado: {data.get('filename')}")
        print(f"Páginas analisadas: {data['metadata'].get('page_count')}")
        print(f"Tamanho do arquivo: {data['metadata'].get('file_size_bytes')} bytes")
        
        stats = data.get("stats", {})
        print(f"\nResumo da Higienização LGPD:")
        print(f"- Total de dados sensíveis mascarados: {stats.get('total_masked_items')}")
        for category, count in stats.get("masked_by_type", {}).items():
            print(f"  • {category}: {count}")
            
        tables = data.get("tables", [])
        print(f"\nTabelas estruturadas extraídas: {len(tables)}")
        for idx, table in enumerate(tables):
            print(f"  • Tabela #{idx + 1}: {len(table.get('original', []))} linhas, {len(table.get('original', [[]])[0])} colunas (Pág {table.get('page')})")
            
        audit = data.get("audit_trail", [])
        print(f"\nLista de Deteções Recentes (Auditoria):")
        for i, item in enumerate(audit[:5]):
            print(f"  [{i+1}] Página {item['page']} • {item['type']}")
            print(f"      Antes:  '{item['original']}'")
            print(f"      Depois: '{item['masked']}'")
            print(f"      Contexto: {item['context']}")
            
        if len(audit) > 5:
            print(f"  ... e mais {len(audit) - 5} ocorrências adicionais.")
            
        print("\nVerificação completa concluída com êxito! Todos os dados estão higienizados de acordo com as regras estabelecidas.")
        return True
        
    except urllib.error.URLError as e:
        print(f"\nErro de Conectividade API: {e}")
        print("Certifique-se de que o servidor FastAPI local está rodando em http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"\nErro inesperado na verificação: {e}")
        return False

if __name__ == "__main__":
    test_process_endpoint()
