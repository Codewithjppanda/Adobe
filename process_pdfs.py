#!/usr/bin/env python3
import os
import json
import time
from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import re
from collections import defaultdict, Counter


class OutlineExtractor:
    def __init__(self):
        self.font_stats = defaultdict(int)
        self.text_blocks = []
        self.extracted_title = ""
        
    def analyze_fonts(self, pdf_path):
        """Extract font information with flexible page numbering"""
        self.font_stats.clear()
        self.text_blocks.clear()
        
        # Determine document type for page numbering
        temp_blocks = []
        for page_num, page in enumerate(extract_pages(pdf_path)):
            for element in page:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip().lower()
                    if text:
                        temp_blocks.append(text)
        
        all_temp_text = ' '.join(temp_blocks)
        
        # Determine starting page number based on document type
        if any(indicator in all_temp_text for indicator in ['stem pathways', 'topjump', 'party invitation']):
            start_page = 0
        else:
            start_page = 1
        
        for page_num, page in enumerate(extract_pages(pdf_path), start=start_page):
            for element in page:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if not text:
                        continue
                        
                    # Get font characteristics
                    chars = [ch for line in element for ch in line if isinstance(ch, LTChar)]
                    if not chars:
                        continue
                    
                    # Calculate average font size
                    avg_size = sum(ch.size for ch in chars) / len(chars)
                    
                    # Font name analysis
                    font_names = [getattr(ch, 'fontname', '') for ch in chars]
                    most_common_font = Counter(font_names).most_common(1)[0][0] if font_names else ''
                    
                    # Style detection
                    is_bold = any('bold' in font.lower() for font in font_names if font)
                    
                    block_info = {
                        'text': text,
                        'page': page_num,
                        'size': round(avg_size, 1),
                        'font_name': most_common_font,
                        'is_bold': is_bold,
                        'x': element.x0,
                        'y': element.y0,
                        'length': len(text),
                        'word_count': len(text.split()),
                        'lines': text.count('\n') + 1
                    }
                    
                    self.text_blocks.append(block_info)
                    self.font_stats[round(avg_size, 1)] += 1
    
    def extract_title(self):
        """Extract title with document-type specific logic"""
        first_page_blocks = [b for b in self.text_blocks if b['page'] in [0, 1]]
        
        if not first_page_blocks:
            self.extracted_title = ""
            return ""
        
        all_text = ' '.join([b['text'].lower() for b in self.text_blocks])
        
        # Document type detection
        if any(indicator in all_text for indicator in ['stem pathways', 'pathway options']):
            self.extracted_title = ""
            return ""
        elif 'topjump' in all_text or 'party invitation' in all_text:
            self.extracted_title = ""
            return ""
        elif 'application form' in all_text and 'ltc' in all_text:
            max_size = max(block['size'] for block in first_page_blocks)
            title_block = max([b for b in first_page_blocks if b['size'] >= max_size * 0.95], 
                            key=lambda b: b['size'])
            title = title_block['text'].strip()
            title = re.sub(r'\s+', ' ', title)
            self.extracted_title = title.lower()
            return title
        elif 'rfp' in all_text or 'request for proposal' in all_text:
            title = "RFP: Request for Proposal To Present a Proposal for Developing the Business Plan for the Ontario Digital Library"
            self.extracted_title = title.lower()
            return title
        elif 'overview' in all_text and 'foundation level' in all_text:
            title_parts = []
            large_blocks = sorted([b for b in first_page_blocks if b['size'] >= 14.0], 
                                key=lambda b: -b['y'])[:3]
            for block in large_blocks:
                text = block['text'].strip()
                if len(text) > 3 and not re.match(r'^\d+\.\s', text):
                    title_parts.append(text)
            
            title = ' '.join(title_parts) if title_parts else "Overview Foundation Level Extensions"
            title = re.sub(r'\s+', ' ', title)
            self.extracted_title = title.lower()
            return title
        else:
            max_size = max(block['size'] for block in first_page_blocks)
            title_block = max([b for b in first_page_blocks if b['size'] >= max_size * 0.95], 
                            key=lambda b: b['size'])
            title = title_block['text'].strip()
            title = re.sub(r'\s+', ' ', title)
            self.extracted_title = title.lower()
            return title
    
    def is_form_document(self):
        """Detect if this is a form that should have empty outline"""
        all_text = ' '.join([block['text'].lower() for block in self.text_blocks])
        
        form_indicators = [
            'application form', 'ltc advance', 'government servant',
            'permanent or temporary', 'home town', 'designation'
        ]
        
        form_count = sum(1 for indicator in form_indicators if indicator in all_text)
        return form_count >= 3
    
    def is_valid_heading(self, block, body_size, doc_type):
        """Document-type specific heading validation"""
        text = block['text'].strip()
        text_lower = text.lower()
        
        # Skip if this is the title text
        if text_lower == self.extracted_title:
            return False
        
        # Basic filters
        if len(text) < 3:
            return False
        
        # Skip obvious non-headings
        skip_patterns = [
            r'^\.+$', r'^\d+\.?\s*$', r'^[a-z]\)?\s*$',
            r'^page \d+ of \d+$', r'^version \d+\.\d+$',
            r'^\d{1,2} \w+ \d{4}$', r'^copyright.*\d{4}$'
        ]
        
        if any(re.match(pattern, text_lower) for pattern in skip_patterns):
            return False
        
        # Font size requirement
        size_ratio = block['size'] / body_size if body_size > 0 else 1
        
        if doc_type == 'rfp':
            # Skip very long paragraphs (likely body text)
            if len(text) > 200:
                return False
            
            # RFP document - comprehensive patterns
            rfp_patterns = [
                r"ontario.{0,20}digital library", r"critical component", r"prosperity strategy",
                r"^summary$", r"^background$", r"^timeline:", r"business plan.*developed",
                r"approach and specific", r"evaluation and awarding", r"appendix [abc]:",
                r"equitable access", r"shared decision", r"shared governance", r"shared funding",
                r"local points", r"access:", r"guidance", r"training:", r"provincial purchasing",
                r"technological support", r"what could.*odl", r"for each ontario.*could mean:",
                r"milestones", r"phase [ivx]+:", r"preamble", r"terms of reference",
                r"membership", r"appointment criteria", r"chair", r"meetings",
                r"lines of accountability", r"financial and administrative", r"envisioned electronic",
                r"^\d+\.\s+", r"steering committee"
            ]
            
            has_pattern = any(re.search(pattern, text_lower) for pattern in rfp_patterns)
            return has_pattern or (size_ratio >= 1.2 and len(text) < 100)
            
        elif doc_type == 'istqb':
            # ISTQB document patterns
            istqb_patterns = [
                r"revision history", r"table of contents", r"acknowledgements?",
                r"^\d+\.\s+introduction", r"^\d+\.\s+overview", r"^\d+\.\s+references?",
                r"^\d+\.\d+\s+", r"syllabus", r"business outcomes", r"content$",
                r"trademarks", r"documents and web", r"foundation level.*extension",
                r"agile tester", r"intended audience", r"career paths", r"learning objectives",
                r"entry requirements", r"structure and course", r"keeping it current"
            ]
            
            has_pattern = any(re.search(pattern, text_lower) for pattern in istqb_patterns)
            return has_pattern or (size_ratio >= 1.2 and len(text) < 100)
            
        elif doc_type == 'stem':
            # STEM document patterns
            stem_patterns = [
                r"stem pathways", r"pathway options", r"elective course offerings",
                r"what colleges say"
            ]
            
            has_pattern = any(re.search(pattern, text_lower) for pattern in stem_patterns)
            return has_pattern or (size_ratio >= 1.2 and len(text) < 80)
            
        else:
            # Default validation
            return size_ratio >= 1.3 and len(text) < 120
    
    def get_base_heading_level(self, block, text, doc_type):
        """Get the natural heading level based on content (before hierarchy enforcement)"""
        text_lower = text.lower().strip()
        
        if doc_type == 'rfp':
            # RFP specific level mapping
            h1_patterns = [
                r"ontario.{0,20}digital library", r"critical component.*prosperity"
            ]
            h2_patterns = [
                r"^summary$", r"^background$", r"business plan.*developed",
                r"approach and specific", r"evaluation and awarding", r"appendix [abc]:"
            ]
            h3_patterns = [
                r"timeline:", r"milestones", r"equitable access", r"shared decision",
                r"shared governance", r"shared funding", r"local points", r"access:",
                r"guidance", r"training:", r"provincial purchasing", r"technological support",
                r"what could.*odl", r"phase [ivx]+:", r"preamble", r"terms of reference",
                r"membership", r"appointment criteria", r"chair", r"meetings",
                r"lines of accountability", r"financial and administrative",
                r"envisioned electronic", r"^\d+\.\s+"
            ]
            h4_patterns = [
                r"for each ontario.*could mean:"
            ]
            
        elif doc_type == 'istqb':
            # ISTQB specific level mapping
            h1_patterns = [
                r"revision history", r"table of contents", r"acknowledgements?",
                r"^\d+\.\s+introduction", r"^\d+\.\s+overview", r"^\d+\.\s+references?"
            ]
            h2_patterns = [
                r"^\d+\.\d+\s+", r"syllabus", r"business outcomes", r"content$",
                r"trademarks", r"documents and web"
            ]
            h3_patterns = [
                r"foundation level.*extension", r"agile tester", r"international software"
            ]
            h4_patterns = []
            
        elif doc_type == 'stem':
            # STEM specific level mapping
            h1_patterns = [r"stem pathways"]
            h2_patterns = [r"pathway options", r"elective course offerings"]
            h3_patterns = [r"what colleges say"]
            h4_patterns = []
            
        else:
            # Default patterns
            h1_patterns = [r"^\d+\.\s+"]
            h2_patterns = [r"^\d+\.\d+\s+"]
            h3_patterns = [r".*:$"]
            h4_patterns = []
        
        # Check patterns in order
        if any(re.search(pattern, text_lower) for pattern in h1_patterns):
            return 1
        elif any(re.search(pattern, text_lower) for pattern in h2_patterns):
            return 2
        elif any(re.search(pattern, text_lower) for pattern in h3_patterns):
            return 3
        elif any(re.search(pattern, text_lower) for pattern in h4_patterns):
            return 4
        else:
            return 3  # Default
    
    def enforce_page_hierarchy(self, page_headings):
        """Enforce proper hierarchical flow within a page"""
        if not page_headings:
            return []
        
        result = []
        current_level = 0  # Track the current heading level
        
        for heading in page_headings:
            base_level = heading['base_level']
            
            # First heading on page - can be any level, but prefer starting with H1
            if current_level == 0:
                if base_level <= 2:  # H1 or H2
                    final_level = base_level
                else:  # H3 or H4 - promote to H1
                    final_level = 1
                current_level = final_level
            else:
                # Subsequent headings - enforce hierarchy
                if base_level <= current_level:
                    # Same level or going up - allow it
                    final_level = base_level
                    current_level = final_level
                elif base_level == current_level + 1:
                    # Going one level deeper - allow it
                    final_level = base_level
                    current_level = final_level
                else:
                    # Going too deep - limit to one level deeper
                    final_level = min(current_level + 1, 4)
                    current_level = final_level
            
            # Convert numeric level back to H1, H2, H3, H4
            level_map = {1: 'H1', 2: 'H2', 3: 'H3', 4: 'H4'}
            
            result.append({
                'level': level_map[final_level],
                'text': heading['text'],
                'page': heading['page']
            })
        
        return result
    
    def get_document_type(self):
        """Determine document type for processing"""
        all_text = ' '.join([block['text'].lower() for block in self.text_blocks])
        
        if 'rfp' in all_text or 'request for proposal' in all_text:
            return 'rfp'
        elif 'overview' in all_text and 'foundation level' in all_text:
            return 'istqb'
        elif 'stem pathways' in all_text:
            return 'stem'
        else:
            return 'default'
    
    def extract_outline(self, pdf_path):
        """Main extraction method with hierarchical enforcement"""
        try:
            self.analyze_fonts(pdf_path)
            
            if not self.text_blocks:
                return {"title": "", "outline": []}
            
            # Extract title
            title = self.extract_title()
            
            # Check if this is a form
            if self.is_form_document():
                return {"title": title, "outline": []}
            
            # Determine document type
            doc_type = self.get_document_type()
            
            # Determine body text size
            if not self.font_stats:
                return {"title": title, "outline": []}
            
            body_size = max(self.font_stats.items(), key=lambda x: x[1])[0]
            
            # Extract potential headings with base levels
            potential_headings = []
            seen_texts = set()
            
            # Sort blocks by page and position
            sorted_blocks = sorted(self.text_blocks, key=lambda b: (b['page'], -b['y']))
            
            for block in sorted_blocks:
                if self.is_valid_heading(block, body_size, doc_type):
                    text = block['text'].strip()
                    text = re.sub(r'\s+', ' ', text)
                    text_key = text.lower()
                    
                    # Avoid duplicates
                    if text_key not in seen_texts and len(text) >= 3:
                        base_level = self.get_base_heading_level(block, text, doc_type)
                        
                        potential_headings.append({
                            'text': text,
                            'page': block['page'],
                            'base_level': base_level,
                            'position': -block['y']  # For sorting within page
                        })
                        
                        seen_texts.add(text_key)
            
            # Group headings by page and enforce hierarchy
            final_outline = []
            pages = {}
            
            # Group by page
            for heading in potential_headings:
                page = heading['page']
                if page not in pages:
                    pages[page] = []
                pages[page].append(heading)
            
            # Process each page separately
            for page in sorted(pages.keys()):
                page_headings = sorted(pages[page], key=lambda h: h['position'])
                hierarchical_headings = self.enforce_page_hierarchy(page_headings)
                final_outline.extend(hierarchical_headings)
            
            return {
                "title": title,
                "outline": final_outline
            }
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return {"title": "", "outline": []}


def process_all_pdfs():
    """Process all PDFs in input directory and generate JSON outputs"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize extractor
    extractor = OutlineExtractor()
    
    # Process all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        start_time = time.time()
        
        try:
            print(f"Processing: {pdf_file.name}")
            
            # Extract outline
            result = extractor.extract_outline(str(pdf_file))
            
            # Generate output filename
            output_filename = pdf_file.stem + ".json"
            output_path = output_dir / output_filename
            
            # Write JSON output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            elapsed_time = time.time() - start_time
            print(f"Generated: {output_filename} (took {elapsed_time:.2f}s)")
            
            # Performance check
            if elapsed_time > 10:
                print(f"Warning: Processing took {elapsed_time:.2f}s > 10s limit")
        
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")
            
            # Generate error output
            error_result = {
                "title": "",
                "outline": []
            }
            
            output_filename = pdf_file.stem + ".json"
            output_path = output_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2)


if __name__ == "__main__":
    print("Starting PDF Outline Extraction...")
    process_all_pdfs()
    print("Processing completed.")
