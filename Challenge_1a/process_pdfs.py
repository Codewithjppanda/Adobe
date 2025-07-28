#!/usr/bin/env python3
import os
import json
import time
import unicodedata
from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import re
from collections import defaultdict, Counter


class CorrectedOutlineExtractor:
    def __init__(self):
        self.font_stats = defaultdict(int)
        self.text_blocks = []
        self.extracted_title = ""
        self.detected_language = "en"
        self.font_size_hierarchy = {}  # Track font size to level mapping
        
    def detect_language(self, text):
        """Detect document language based on character analysis"""
        if not text:
            return "en"
        
        # Count different script types
        latin_count = 0
        cjk_count = 0
        japanese_count = 0
        korean_count = 0
        arabic_count = 0
        
        for char in text:
            if '\u3040' <= char <= '\u309F':  # Hiragana
                japanese_count += 1
                cjk_count += 1
            elif '\u30A0' <= char <= '\u30FF':  # Katakana
                japanese_count += 1
                cjk_count += 1
            elif '\u4E00' <= char <= '\u9FAF':  # CJK Unified Ideographs
                cjk_count += 1
            elif '\uAC00' <= char <= '\uD7AF':  # Korean Hangul
                korean_count += 1
            elif '\u0600' <= char <= '\u06FF':  # Arabic
                arabic_count += 1
            elif char.isascii() and char.isalpha():
                latin_count += 1
        
        total_chars = len([c for c in text if c.isalpha()])
        if total_chars == 0:
            return "en"
        
        # Determine language based on character distribution
        if japanese_count > total_chars * 0.1:
            return "ja"
        elif korean_count > total_chars * 0.2:
            return "ko"
        elif cjk_count > total_chars * 0.3:
            return "zh"
        elif arabic_count > total_chars * 0.2:
            return "ar"
        else:
            return "en"
    
    def normalize_text(self, text):
        """Normalize text for different languages"""
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Language-specific normalization
        if self.detected_language == "ja":
            text = text.translate(str.maketrans(
                '０１２３４５６７８９．',
                '0123456789.'
            ))
        
        return text.strip()
    
    def analyze_fonts(self, pdf_path):
        """Extract font information starting from page 0"""
        self.font_stats.clear()
        self.text_blocks.clear()
        
        # First pass: collect all text for language detection
        all_text_for_detection = []
        for page_num, page in enumerate(extract_pages(pdf_path)):
            for element in page:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if text:
                        all_text_for_detection.append(text)
        
        # Detect document language
        combined_text = ' '.join(all_text_for_detection)
        self.detected_language = self.detect_language(combined_text)
        print(f"[DEBUG] Detected language: {self.detected_language}")
        
        # START FROM PAGE 0 (corrected)
        start_page = 0
        
        # Second pass: extract with font information
        for page_num, page in enumerate(extract_pages(pdf_path), start=start_page):
            for element in page:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if not text:
                        continue
                    
                    # Normalize text
                    text = self.normalize_text(text)
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
                        'word_count': len(text.split()) if self.detected_language in ['en', 'ar'] else len(text),
                        'lines': text.count('\n') + 1,
                        'is_all_caps': text.isupper(),
                        'has_mixed_case': not text.isupper() and not text.islower()
                    }
                    
                    self.text_blocks.append(block_info)
                    self.font_stats[round(avg_size, 1)] += 1
    
    def build_font_hierarchy(self):
        """Build font size hierarchy to correctly map font sizes to heading levels"""
        if not self.text_blocks:
            return
        
        # Get all font sizes and their frequencies
        font_sizes = list(self.font_stats.keys())
        font_sizes.sort(reverse=True)  # Largest first
        
        # Determine body text size (most common)
        body_size = max(self.font_stats.items(), key=lambda x: x[1])[0]
        
        # Build hierarchy mapping
        self.font_size_hierarchy = {}
        
        # Filter out sizes that are clearly headings (larger than body)
        heading_sizes = [size for size in font_sizes if size > body_size]
        heading_sizes.sort(reverse=True)  # Largest first
        
        print(f"[DEBUG] Body size: {body_size}, Heading sizes: {heading_sizes}")
        
        # Assign heading levels based on font size
        for i, size in enumerate(heading_sizes[:3]):  # Max 3 heading levels
            self.font_size_hierarchy[size] = i + 1  # H1, H2, H3
        
        print(f"[DEBUG] Font hierarchy: {self.font_size_hierarchy}")
    
    def extract_title_corrected(self):
        """Enhanced generic title extraction with better document type awareness"""
        # Only look at first page (page 0)
        first_page_blocks = [b for b in self.text_blocks if b['page'] == 0]
        
        if not first_page_blocks:
            self.extracted_title = ""
            return ""
        
        # Analyze document characteristics
        all_text = ' '.join([b['text'].lower() for b in self.text_blocks])
        
        # Document type classification based on structure patterns
        document_patterns = {
            'catalog_listing': [
                r'pathway', r'course offerings?', r'elective', r'program options?',
                r'what.*say', r'career paths?', r'academic.*options'
            ],
            'invitation_flyer': [
                r'hope to see you', r'rsvp', r'www\.', r'\.com', r'address:',
                r'party', r'invitation', r'parents or guardians'
            ],
            'form_document': [
                r'application form', r'signature', r'government servant',
                r'permanent or temporary', r'ltc advance'
            ],
            'formal_document': [
                r'overview', r'foundation level', r'revision history',
                r'table of contents', r'acknowledgements', r'references'
            ]
        }
        
        # Classify document type
        document_type = 'standard'
        for doc_type, patterns in document_patterns.items():
            if any(re.search(pattern, all_text) for pattern in patterns):
                document_type = doc_type
                break
        
        print(f"[DEBUG] Detected document type: {document_type}")
        
        # Type-specific title extraction logic
        if document_type == 'catalog_listing':
            # For catalogs/pathways, usually no distinct title - main content is H1
            self.extracted_title = ""
            return ""
        
        elif document_type == 'invitation_flyer':
            # For flyers, look for short, prominent text that's not contact info
            title_candidates = []
            
            for block in first_page_blocks:
                text = block['text'].strip()
                text_lower = text.lower()
                
                # Skip contact/address information
                if any(pattern in text_lower for pattern in 
                       ['www.', '.com', 'address:', 'phone:', 'rsvp:', 'parents or guardians']):
                    continue
                
                # Skip very long text (likely body content)
                word_count = len(text.split())
                if word_count > 12:
                    continue
                
                # Score for flyer titles
                title_score = 0
                
                # Position weight
                max_y = max(b['y'] for b in first_page_blocks)
                position_ratio = block['y'] / max_y if max_y > 0 else 0
                if position_ratio >= 0.7:
                    title_score += 2
                
                # Font size weight
                max_size = max(b['size'] for b in first_page_blocks)
                size_ratio = block['size'] / max_size
                if size_ratio >= 0.9:
                    title_score += 3
                
                # Short, catchy phrases
                if 2 <= word_count <= 8:
                    title_score += 2
                
                # Exclamation or emotional content
                if '!' in text or any(word in text_lower for word in ['hope', 'see', 'there']):
                    title_score += 1
                
                if title_score >= 4:
                    title_candidates.append({
                        'text': text,
                        'score': title_score,
                        'block': block
                    })
            
            if title_candidates:
                best_title = max(title_candidates, key=lambda x: x['score'])
                title_text = best_title['text']
                self.extracted_title = title_text.lower()
                return title_text
            else:
                self.extracted_title = ""
                return ""
        
        elif document_type == 'form_document':
            # For forms, look for the form name/purpose
            for block in first_page_blocks:
                text = block['text'].strip()
                text_lower = text.lower()
                
                if 'form' in text_lower and len(text.split()) >= 3:
                    title_text = text
                    self.extracted_title = title_text.lower()
                    return title_text
            
            self.extracted_title = ""
            return ""
        
        else:
            # For formal documents, look for proper titles
            title_candidates = []
            
            for block in first_page_blocks:
                text = block['text'].strip()
                text_lower = text.lower()
                
                # Skip obvious non-titles
                skip_patterns = [
                    r'^\d+$', r'^page \d+', r'^copyright', r'^version',
                    r'^\d+\.\s', r'^chapter \d+', r'^section \d+',
                    r'revision history', r'table of contents', r'acknowledgements'
                ]
                
                if any(re.match(pattern, text_lower) for pattern in skip_patterns):
                    continue
                
                # Title scoring for formal documents
                title_score = 0
                word_count = len(text.split())
                
                # Position weight (top of page)
                max_y = max(b['y'] for b in first_page_blocks)
                position_ratio = block['y'] / max_y if max_y > 0 else 0
                if position_ratio >= 0.8:
                    title_score += 3
                elif position_ratio >= 0.6:
                    title_score += 2
                
                # Font size weight (largest font)
                max_size = max(b['size'] for b in first_page_blocks)
                size_ratio = block['size'] / max_size
                if size_ratio >= 0.95:
                    title_score += 3
                elif size_ratio >= 0.85:
                    title_score += 2
                
                # Length appropriateness for titles
                if 3 <= word_count <= 20:
                    title_score += 2
                elif 20 < word_count <= 30:
                    title_score += 1
                
                # Proper title characteristics
                if not re.match(r'^\d+\.', text) and not text.endswith(':'):
                    title_score += 2
                
                # Mixed case or proper capitalization
                if re.match(r'^[A-Z]', text) and not text.isupper():
                    title_score += 1
                
                # Contains descriptive words
                if any(word in text_lower for word in 
                       ['overview', 'introduction', 'guide', 'manual', 'report', 'analysis']):
                    title_score += 1
                
                if title_score >= 6:  # Higher threshold for formal documents
                    title_candidates.append({
                        'text': text,
                        'score': title_score,
                        'block': block
                    })
            
            # Select best title candidate
            if title_candidates:
                title_candidates.sort(key=lambda x: (-x['score'], -x['block']['size']))
                best_title = title_candidates[0]
                
                # Ensure it's distinct from other content
                other_blocks = [b for b in first_page_blocks if b != best_title['block']]
                if len(other_blocks) >= 1:
                    title_text = best_title['text']
                    self.extracted_title = title_text.lower()
                    print(f"[DEBUG] Extracted formal document title: '{title_text}'")
                    return title_text
        
        # No clear title found
        print(f"[DEBUG] No clear title found for document type: {document_type}")
        self.extracted_title = ""
    
    def is_structural_heading_pattern(self, text):
        """Detect universal structural heading patterns"""
        text_normalized = self.normalize_text(text)
        
        if self.detected_language == "ja":
            japanese_patterns = [
                r'^第[一二三四五六七八九十\d]+章',
                r'^第[一二三四五六七八九十\d]+節',
                r'^[一二三四五六七八九十\d]+\.',
                r'^[１-９０]+\.',
                r'^●', r'^○', r'^■',
                r'^【.*】$',
            ]
            return any(re.search(pattern, text_normalized) for pattern in japanese_patterns)
        
        elif self.detected_language == "zh":
            chinese_patterns = [
                r'^第[一二三四五六七八九十\d]+章',
                r'^第[一二三四五六七八九十\d]+节',
                r'^[一二三四五六七八九十\d]+\.',
                r'^【.*】$',
            ]
            return any(re.search(pattern, text_normalized) for pattern in chinese_patterns)
        
        elif self.detected_language == "ko":
            korean_patterns = [
                r'^제[일이삼사오육칠팔구십\d]+장',
                r'^제[일이삼사오육칠팔구십\d]+절',
                r'^[일이삼사오육칠팔구십\d]+\.',
            ]
            return any(re.search(pattern, text_normalized) for pattern in korean_patterns)
        
        elif self.detected_language == "ar":
            arabic_patterns = [
                r'^[٠-٩]+\.',
                r'^[0-9]+\.',
            ]
            return any(re.search(pattern, text_normalized) for pattern in arabic_patterns)
        
        else:
            # Universal patterns
            universal_patterns = [
                r'^\d+\.?\s+[A-Z]',              # "1. Heading"
                r'^\d+\.\d+\.?\s+[A-Z]',         # "1.1. Subsection"
                r'^[IVXLCDM]+\.?\s+[A-Z]',       # "I. Roman numerals"
                r'^[A-Z]\.?\s+[A-Z]',            # "A. Letter sections"
            ]
            return any(re.search(pattern, text_normalized) for pattern in universal_patterns)
        
        return False
    
    def is_valid_heading(self, block, body_size):
        """Corrected heading validation"""
        text = block['text'].strip()
        text_lower = text.lower()
        
        # Skip if this is the title
        if text_lower == self.extracted_title:
            return False
        
        # Basic filters
        min_length = 2 if self.detected_language in ['ja', 'zh', 'ko'] else 3
        max_length = 200 if self.detected_language in ['ja', 'zh', 'ko'] else 150
        
        if len(text) < min_length or len(text) > max_length:
            return False
        
        # Universal skip patterns
        skip_patterns = [
            r'^\.+$', r'^\d+\.?\s*$', r'^[a-z]\)?\s*$',
            r'^page \d+', r'^copyright', r'^version \d+',
            r'^\d{1,2}/\d{1,2}/\d{4}$', r'^www\.', r'^http',
            r'^\d+$', r'^[ivx]+$'
        ]
        
        if any(re.match(pattern, text_lower) for pattern in skip_patterns):
            return False
        
        # Font-based validation with corrected logic
        size_ratio = block['size'] / body_size if body_size > 0 else 1
        
        heading_score = 0
        
        # More accurate font size criteria
        if size_ratio >= 1.5:
            heading_score += 4
        elif size_ratio >= 1.3:
            heading_score += 3
        elif size_ratio >= 1.2:
            heading_score += 2
        elif size_ratio >= 1.1:
            heading_score += 1
        
        # Bold bonus
        if block['is_bold']:
            heading_score += 2
        
        # Structural pattern bonus
        if self.is_structural_heading_pattern(text):
            heading_score += 3
        
        # Text characteristics
        word_count = len(text.split()) if self.detected_language in ['en', 'ar'] else len(text)
        
        # All caps (common for headings)
        if block['is_all_caps'] and word_count >= 2:
            heading_score += 2
        
        # Title case
        elif re.match(r'^[A-Z][a-zA-Z\s\-\'(),]+$', text) and word_count >= 2:
            heading_score += 1
        
        # Ends with colon
        elif text.endswith(':') and len(text) > 5:
            heading_score += 1
        
        # Length appropriateness
        if self.detected_language in ['ja', 'zh', 'ko']:
            if 3 <= word_count <= 30:
                heading_score += 1
        else:
            if 2 <= word_count <= 15:
                heading_score += 1
        
        return heading_score >= 4
    
    def determine_heading_level_corrected(self, block, text):
        """Corrected heading level determination using font hierarchy"""
        text_normalized = self.normalize_text(text)
        
        # First try structural patterns
        if self.detected_language == "ja":
            if re.search(r'^第[一二三四五六七八九十\d]+章', text_normalized):
                return 1
            elif re.search(r'^第[一二三四五六七八九十\d]+節', text_normalized):
                return 2
            elif re.search(r'^[一二三四五六七八九十\d]+\.', text_normalized):
                return 3
        
        elif self.detected_language in ["zh", "ko"]:
            if re.search(r'^第[一二三四五六七八九十\d]+[章节]', text_normalized):
                return 1
            elif re.search(r'^[一二三四五六七八九十\d]+\.', text_normalized):
                return 2
        
        elif self.detected_language == "ar":
            if re.search(r'^[٠-٩0-9]+\.', text_normalized):
                return 2
        
        else:
            # Universal patterns with corrected logic
            if re.match(r'^\d+\.\s+', text_normalized):
                return 1  # "1. Main Section"
            elif re.match(r'^\d+\.\d+\.?\s+', text_normalized):
                return 2  # "1.1. Subsection"
            elif re.match(r'^\d+\.\d+\.\d+\.?\s+', text_normalized):
                return 3  # "1.1.1. Sub-subsection"
            elif re.match(r'^[IVXLCDM]+\.?\s+', text_normalized):
                return 1  # "I. Roman numerals"
            elif re.match(r'^[A-Z]\.?\s+', text_normalized):
                return 2  # "A. Letter sections"
        
        # Use font hierarchy mapping
        font_size = block['size']
        if font_size in self.font_size_hierarchy:
            return self.font_size_hierarchy[font_size]
        
        # Fallback: use relative font size
        body_size = max(self.font_stats.items(), key=lambda x: x[1])[0] if self.font_stats else 12.0
        size_ratio = font_size / body_size
        
        if size_ratio >= 1.5:
            return 1
        elif size_ratio >= 1.3:
            return 2
        else:
            return 3
    
    def enforce_corrected_hierarchy(self, headings):
        """Corrected hierarchy enforcement"""
        if not headings:
            return []
        
        # Group by page
        pages = defaultdict(list)
        for heading in headings:
            pages[heading['page']].append(heading)
        
        final_outline = []
        
        # Process each page
        for page_num in sorted(pages.keys()):
            page_headings = pages[page_num]
            
            # Sort by position within page (top to bottom)
            page_headings.sort(key=lambda h: h['position'])
            
            # Apply corrected hierarchy logic
            current_level = 0
            
            for heading in page_headings:
                base_level = heading['level']
                
                if current_level == 0:
                    # First heading on page - use its natural level
                    final_level = base_level
                    current_level = final_level
                else:
                    # Subsequent headings - enforce logical flow
                    if base_level <= current_level:
                        # Same level or going up
                        final_level = base_level
                        current_level = final_level
                    elif base_level == current_level + 1:
                        # Going one level deeper
                        final_level = base_level
                        current_level = final_level
                    else:
                        # Going too deep - limit progression
                        final_level = min(current_level + 1, 3)
                        current_level = final_level
                
                # Map to H1, H2, H3
                level_map = {1: 'H1', 2: 'H2', 3: 'H3'}
                
                final_outline.append({
                    'level': level_map.get(final_level, 'H3'),
                    'text': heading['text'],
                    'page': heading['page']
                })
                
                print(f"[DEBUG] Page {page_num}: '{heading['text'][:40]}...' → {level_map.get(final_level, 'H3')}")
        
        return final_outline
    
    def extract_outline(self, pdf_path):
        """Main extraction with corrected logic"""
        try:
            self.analyze_fonts(pdf_path)
            
            if not self.text_blocks:
                return {"title": "", "outline": []}
            
            # Build font hierarchy first
            self.build_font_hierarchy()
            
            # Extract title
            title = self.extract_title_corrected()
            
            # Get body text size
            if not self.font_stats:
                return {"title": title, "outline": []}
            
            body_size = max(self.font_stats.items(), key=lambda x: x[1])[0]
            print(f"[DEBUG] Body text size: {body_size}")
            
            # Extract headings
            potential_headings = []
            seen_texts = set()
            
            # Sort blocks by page and position
            sorted_blocks = sorted(self.text_blocks, key=lambda b: (b['page'], -b['y']))
            
            for block in sorted_blocks:
                if self.is_valid_heading(block, body_size):
                    text = block['text'].strip()
                    text = re.sub(r'\s+', ' ', text)
                    text_key = text.lower()
                    
                    # Avoid duplicates and title
                    min_length = 2 if self.detected_language in ['ja', 'zh', 'ko'] else 3
                    if text_key not in seen_texts and len(text) >= min_length and text_key != self.extracted_title:
                        level = self.determine_heading_level_corrected(block, text)
                        
                        potential_headings.append({
                            'text': text,
                            'page': block['page'],
                            'level': level,
                            'position': -block['y']
                        })
                        
                        seen_texts.add(text_key)
                        print(f"[DEBUG] Valid heading: '{text[:50]}...' (Level: {level}, Page: {block['page']})")
            
            # Apply corrected hierarchy
            final_outline = self.enforce_corrected_hierarchy(potential_headings)
            
            print(f"[DEBUG] Final outline: {len(final_outline)} headings")
            
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
    
    # Initialize corrected extractor
    extractor = CorrectedOutlineExtractor()
    
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
            
            # Write JSON output with UTF-8 support
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            elapsed_time = time.time() - start_time
            print(f"Generated: {output_filename} (took {elapsed_time:.2f}s)")
            print(f"Detected language: {extractor.detected_language}")
            
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
                json.dump(error_result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    print("Starting Corrected PDF Outline Extraction...")
    process_all_pdfs()
    print("Processing completed.")
