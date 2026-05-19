import re

# ==========================================
# LGPD / PII Validation Algorithms
# ==========================================

def validate_cpf(cpf_str: str) -> bool:
    """Validates a Brazilian CPF using checksum calculation."""
    # Remove all non-digits
    digits = [int(d) for d in cpf_str if d.isdigit()]
    if len(digits) != 11:
        return False
    
    # Check for known invalid sequences of identical digits
    if len(set(digits)) == 1:
        return False
    
    # Calculate first checksum digit
    sum1 = sum(digits[i] * (10 - i) for i in range(9))
    digit1 = (sum1 * 10) % 11
    if digit1 == 10:
        digit1 = 0
        
    # Calculate second checksum digit
    sum2 = sum(digits[i] * (11 - i) for i in range(10))
    digit2 = (sum2 * 10) % 11
    if digit2 == 10:
        digit2 = 0
        
    return digits[9] == digit1 and digits[10] == digit2


def validate_cnpj(cnpj_str: str) -> bool:
    """Validates a Brazilian CNPJ using checksum calculation."""
    # Remove all non-digits
    digits = [int(d) for d in cnpj_str if d.isdigit()]
    if len(digits) != 14:
        return False
        
    # Check for known invalid sequences of identical digits
    if len(set(digits)) == 1:
        return False
        
    # Calculate first checksum digit
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum1 = sum(digits[i] * weights1[i] for i in range(12))
    digit1 = sum1 % 11
    digit1 = 0 if digit1 < 2 else 11 - digit1
    
    # Calculate second checksum digit
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum2 = sum(digits[i] * weights2[i] for i in range(13))
    digit2 = sum2 % 11
    digit2 = 0 if digit2 < 2 else 11 - digit2
    
    return digits[12] == digit1 and digits[13] == digit2


# ==========================================
# Custom Masking Helper Functions
# ==========================================

def get_masked_cpf(cpf_match: str) -> str:
    """Masks a CPF partially, keeping formatting: 123.***.***-45."""
    digits = "".join(d for d in cpf_match if d.isdigit())
    if len(digits) == 11:
        return f"{digits[0:3]}.***.***-{digits[9:11]}"
    return "[CPF MASCARADO]"


def get_masked_cnpj(cnpj_match: str) -> str:
    """Masks a CNPJ partially: 12.***.***/0001-90."""
    digits = "".join(d for d in cnpj_match if d.isdigit())
    if len(digits) == 14:
        return f"{digits[0:2]}.***.***/{digits[8:12]}-{digits[12:14]}"
    return "[CNPJ MASCARADO]"


def get_masked_email(email_match: str) -> str:
    """Masks an email partially: u***s@domain.com."""
    try:
        user, domain = email_match.split('@', 1)
        if len(user) <= 2:
            masked_user = user[0] + "*"
        else:
            masked_user = user[0] + "***" + user[-1]
        return f"{masked_user}@{domain}"
    except Exception:
        return "[EMAIL MASCARADO]"


def get_masked_phone(phone_match: str) -> str:
    """Masks a phone number partially: (XX) 9****-XXXX."""
    digits = "".join(d for d in phone_match if d.isdigit())
    # Strip country code 55 if present
    if digits.startswith("55") and len(digits) > 10:
        digits = digits[2:]
        
    if len(digits) == 11:  # Mobile with 9
        return f"({digits[0:2]}) {digits[2]}****-{digits[7:11]}"
    elif len(digits) == 10:  # Landline
        return f"({digits[0:2]}) ****-{digits[6:10]}"
    elif len(digits) == 9:  # No DDD mobile
        return f"{digits[0]}****-{digits[5:9]}"
    elif len(digits) == 8:  # No DDD landline
        return f"****-{digits[4:8]}"
    return "[TELEFONE MASCARADO]"


def get_masked_bank(bank_match: str) -> str:
    """Masks bank details while keeping the keyword structure."""
    # We want to identify the digits in bank details and mask them.
    # Ex: "Agência: 1234-5" -> "Agência: ****-*"
    # Ex: "C/C: 12345-6" -> "C/C: *****-*"
    # We replace any sequence of digits followed by an optional dash and digit/X with asterisks.
    masked = bank_match
    
    # 1. Match Agência pattern: "Agência 1234-5" or "Agência: 1234"
    def repl_digits(m):
        val = m.group(0)
        # replace all digits with *
        return re.sub(r'\d', '*', val)
        
    # Search and replace numbers inside bank matches
    masked = re.sub(r'\b\d{1,6}(?:-\d|-[xX])?\b', repl_digits, masked)
    masked = re.sub(r'\b\d{4,12}\b', repl_digits, masked)
    return masked


# ==========================================
# Core Sanitizer Engine
# ==========================================

class LGPDSanitizer:
    def __init__(self):
        # We pre-compile standard regex patterns.
        # CPF formatted and unformatted
        self.cpf_pattern = re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b')
        
        # CNPJ formatted and unformatted
        self.cnpj_pattern = re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{14}\b')
        
        # Email standard pattern
        self.email_pattern = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
        
        # Phone: matches various Brazilian phone patterns
        self.phone_pattern = re.compile(
            r'\+?55\s?\(?\d{2}\)?\s?9\d{4}-\d{4}'       # +55 (11) 91234-5678
            r'|\+?55\s?\d{2}\s?9\d{8}'                   # +5511912345678
            r'|\(?\d{2}\)?\s?9\d{4}-\d{4}'               # (11) 91234-5678
            r'|\(?\d{2}\)?\s?9\d{8}'                     # (11) 912345678
            r'|\b9\d{4}-\d{4}\b'                         # 91234-5678 (local)
            r'|\b\d{4}-\d{4}\b'                          # 1234-5678 (landline)
            r'|\b\d{10,11}\b'                            # Plain 10 or 11 digits (if not CPF/CNPJ)
        )
        
        # Bank Details: search for keys like Agência, Conta followed by numbers
        # Matches patterns like "Agência: 1234-5", "c/c: 12345-6", "Banco do Brasil AG 1234 CC 12345"
        self.bank_pattern = re.compile(
            r'(?:ag[eê]ncia|ag\.?|c/c|c\.c\.?|conta(?:\s+corrente)?|poupan[çc]a|banco|bco\.?)\s*[:\-–—\s]+\s*\d{1,6}(?:-\d|-[xX])?'
            r'|(?:ag[eê]ncia|ag\.?|c/c|c\.c\.?|conta(?:\s+corrente)?|poupan[çc]a|banco|bco\.?)\s*\d{1,12}(?:-\d|-[xX])?',
            re.IGNORECASE
        )

    def extract_context(self, text: str, start: int, end: int, window: int = 35) -> str:
        """Extracts a snippet of text surrounding a match for auditing purposes."""
        start_pos = max(0, start - window)
        end_pos = min(len(text), end + window)
        
        snippet = text[start_pos:end_pos].replace('\n', ' ')
        prefix = "..." if start_pos > 0 else ""
        suffix = "..." if end_pos < len(text) else ""
        
        return f"{prefix}{snippet}{suffix}"

    def sanitize_text(self, text: str, page_num: int = 1) -> tuple[str, list[dict]]:
        """
        Scans a page of text, identifies sensitive data, masks them,
        and generates a detailed audit trail.
        """
        if not text:
            return "", []

        audit_trail = []
        masked_text = text

        # Helper structure to track already masked spans to prevent overlapping masks
        masked_spans = []

        def is_overlapping(start: int, end: int) -> bool:
            for s_start, s_end in masked_spans:
                if max(start, s_start) < min(end, s_end):
                    return True
            return False

        # --- 1. PROCESS EMAIL ---
        # Emails are unique patterns and rarely collide. Process them first.
        for match in list(self.email_pattern.finditer(text)):
            start, end = match.span()
            matched_val = match.group(0)
            
            # Record span
            masked_spans.append((start, end))
            
            masked_val = get_masked_email(matched_val)
            audit_trail.append({
                "page": page_num,
                "type": "E-mail",
                "original": matched_val,
                "masked": masked_val,
                "context": self.extract_context(text, start, end)
            })

        # --- 2. PROCESS CPF ---
        for match in list(self.cpf_pattern.finditer(text)):
            start, end = match.span()
            matched_val = match.group(0)
            
            if is_overlapping(start, end):
                continue
                
            # Perform checksum validation
            if validate_cpf(matched_val):
                masked_spans.append((start, end))
                masked_val = get_masked_cpf(matched_val)
                audit_trail.append({
                    "page": page_num,
                    "type": "CPF",
                    "original": matched_val,
                    "masked": masked_val,
                    "context": self.extract_context(text, start, end)
                })

        # --- 3. PROCESS CNPJ ---
        for match in list(self.cnpj_pattern.finditer(text)):
            start, end = match.span()
            matched_val = match.group(0)
            
            if is_overlapping(start, end):
                continue
                
            # Perform checksum validation
            if validate_cnpj(matched_val):
                masked_spans.append((start, end))
                masked_val = get_masked_cnpj(matched_val)
                audit_trail.append({
                    "page": page_num,
                    "type": "CNPJ",
                    "original": matched_val,
                    "masked": masked_val,
                    "context": self.extract_context(text, start, end)
                })

        # --- 4. PROCESS BANK DETAILS ---
        for match in list(self.bank_pattern.finditer(text)):
            start, end = match.span()
            matched_val = match.group(0)
            
            if is_overlapping(start, end):
                continue
                
            masked_spans.append((start, end))
            masked_val = get_masked_bank(matched_val)
            audit_trail.append({
                "page": page_num,
                "type": "Dados Bancários",
                "original": matched_val,
                "masked": masked_val,
                "context": self.extract_context(text, start, end)
            })

        # --- 5. PROCESS PHONES ---
        for match in list(self.phone_pattern.finditer(text)):
            start, end = match.span()
            matched_val = match.group(0)
            
            if is_overlapping(start, end):
                continue
                
            # Validate that 10 or 11 plain digits are not actually valid CPFs/CNPJs that weren't masked
            clean_digits = "".join(d for d in matched_val if d.isdigit())
            if len(clean_digits) == 11 and validate_cpf(clean_digits):
                continue
            if len(clean_digits) == 14 and validate_cnpj(clean_digits):
                continue
                
            # If plain digits represent normal numbers like 20260519 or 10000000000, skip to avoid false positives
            # Typically a telephone DDD is between 11 and 99. Let's do a loose validation check.
            if len(clean_digits) == 11 and not clean_digits.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')):
                continue
            
            masked_spans.append((start, end))
            masked_val = get_masked_phone(matched_val)
            audit_trail.append({
                "page": page_num,
                "type": "Telefone",
                "original": matched_val,
                "masked": masked_val,
                "context": self.extract_context(text, start, end)
            })

        # Sort the spans in descending order of start position so that we can replace text
        # from end to beginning without invalidating character offsets!
        # This is a critical algorithmic detail for correct replacement.
        sorted_spans = sorted(zip(masked_spans, audit_trail), key=lambda x: x[0][0], reverse=True)
        
        # Build the masked text string
        masked_list = list(text)
        for (start, end), audit in sorted_spans:
            masked_list[start:end] = list(audit["masked"])
            
        masked_text = "".join(masked_list)

        return masked_text, audit_trail

    def sanitize_cell(self, cell_text: str) -> str:
        """
        Sanitizes a single table cell. Since cells contain very short text,
        we run a simpler direct matching without generating full context logs,
        just replacing found elements.
        """
        if not cell_text:
            return ""
            
        cell_masked = cell_text
        
        # 1. Emails
        for match in list(self.email_pattern.finditer(cell_text)):
            cell_masked = cell_masked.replace(match.group(0), get_masked_email(match.group(0)))
            
        # 2. CPFs
        for match in list(self.cpf_pattern.finditer(cell_text)):
            val = match.group(0)
            if validate_cpf(val):
                cell_masked = cell_masked.replace(val, get_masked_cpf(val))
                
        # 3. CNPJs
        for match in list(self.cnpj_pattern.finditer(cell_text)):
            val = match.group(0)
            if validate_cnpj(val):
                cell_masked = cell_masked.replace(val, get_masked_cnpj(val))
                
        # 4. Bank details
        for match in list(self.bank_pattern.finditer(cell_text)):
            cell_masked = cell_masked.replace(match.group(0), get_masked_bank(match.group(0)))
            
        # 5. Phones
        for match in list(self.phone_pattern.finditer(cell_text)):
            val = match.group(0)
            clean_digits = "".join(d for d in val if d.isdigit())
            if len(clean_digits) == 11 and validate_cpf(clean_digits):
                continue
            cell_masked = cell_masked.replace(val, get_masked_phone(val))
            
        return cell_masked

    def sanitize_table(self, table: list[list[str]]) -> list[list[str]]:
        """Masks sensitive elements in all rows of a 2D table grid."""
        sanitized_table = []
        for row in table:
            sanitized_row = []
            for cell in row:
                if cell is None:
                    sanitized_row.append("")
                else:
                    sanitized_row.append(self.sanitize_cell(str(cell)))
            sanitized_table.append(sanitized_row)
        return sanitized_table
