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


class GenericOutlineExtractor:
    def __init__(self):
        self.font_stats = defaultdict(int)
        self.text_blocks = []
        self.extracted_title = ""
        self.detected_language = "en"
        
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
            # Japanese detection (Hiragana, Katakana, Kanji)
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
            # Japanese: Convert full-width to half-width for numbers/ASCII
            text = text.translate(str.maketrans(
                '０１２３４５６７８９．',
                '0123456789.'
            ))
        
        return text.strip()
    
    def is_universal_heading_pattern(self, text):
        """Detect universal heading patterns (no content-specific logic)"""
        text_normalized = self.normalize_text(text)
        
        if self.detected_language == "ja":
            # Japanese structural patterns only
            japanese_patterns = [
                r'^第[一二三四五六七八九十\d]+章',  # Chapter patterns
                r'^第[一二三四五六七八九十\d]+節',  # Section patterns
                r'^[一二三四五六七八九十\d]+\.',   # Numbered sections
                r'^[１-９０]+\.',                   # Full-width numbers
                r'^●', r'^○', r'^■',               # Bullet points
                r'^【.*】$',                        # Bracketed headings
            ]
            return any(re.search(pattern, text_normalized) for pattern in japanese_patterns)
        
        elif self.detected_language == "zh":
            # Chinese structural patterns
            chinese_patterns = [
                r'^第[一二三四五六七八九十\d]+章',
                r'^第[一二三四五六七八九十\d]+节',
                r'^[一二三四五六七八九十\d]+\.',
                r'^【.*】$',
            ]
            return any(re.search(pattern, text_normalized) for pattern in chinese_patterns)
        
        elif self.detected_language == "ko":
            # Korean structural patterns
            korean_patterns = [
                r'^제[일이삼사오육칠팔구십\d]+장',
                r'^제[일이삼사오육칠팔구십\d]+절',
                r'^[일이삼사오육칠팔구십\d]+\.',
            ]
            return any(re.search(pattern, text_normalized) for pattern in korean_patterns)
        
        elif self.detected_language == "ar":
            # Arabic structural patterns
            arabic_patterns = [
                r'^[٠-٩]+\.',
                r'^[0-9]+\.',
            ]
            return any(re.search(pattern, text_normalized) for pattern in arabic_patterns)
        
        else:
            # Universal Latin/English structural patterns (no content)
            universal_patterns = [
                r'^\d+\.?\s+[A-Z]',              # "1. Heading" or "1 Heading"
                r'^\d+\.\d+\.?\s+[A-Z]',         # "1.1. Subsection"
                r'^[IVXLCDM]+\.?\s+[A-Z]',       # "I. Roman numerals"
                r'^[A-Z]\.?\s+[A-Z]',            # "A. Letter sections"
                r'^Chapter\s+\d+',               # "Chapter 1"
                r'^Section\s+\d+',               # "Section 1"
                r'^Part\s+[IVXLCDM\d]+',        # "Part I" or "Part 1"
            ]
            return any(re.search(pattern, text_normalized) for pattern in universal_patterns)
        
        return False
    
    def analyze_fonts(self, pdf_path):
        """Extract font information with multilingual support"""
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
        
        # Generic page numbering (start from 1 for most documents)
        start_page = 1
        
        # Second pass: extract with font information
        for page_num, page in enumerate(extract_pages(pdf_path), start=start_page):
            for element in page:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if not text:
                        continue
                    
                    # Normalize text for the detected language
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
                    
                    # Universal style detection
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
                        'lines': text.count('\n') + 1
                    }
                    
                    self.text_blocks.append(block_info)
                    self.font_stats[round(avg_size, 1)] += 1
    
    def extract_title(self):
        """Generic title extraction without hardcoded logic"""
        first_page_blocks = [b for b in self.text_blocks if b['page'] == 1]
        
        if not first_page_blocks:
            self.extracted_title = ""
            return ""
        
        # Find largest font size block as title (universal approach)
        max_size = max(block['size'] for block in first_page_blocks)
        title_candidates = [b for b in first_page_blocks if b['size'] >= max_size * 0.95]
        
        if title_candidates:
            # Choose the one with best position (usually top of page)
            title_block = max(title_candidates, key=lambda b: b['y'])
            title = self.normalize_text(title_block['text'])
            title = re.sub(r'\s+', ' ', title)
            self.extracted_title = title.lower()
            return title
        
        return ""
    
    def is_valid_heading(self, block, body_size):
        """Generic heading validation without hardcoded content patterns"""
        text = block['text'].strip()
        text_lower = text.lower()
        
        # Skip if this is the title text
        if text_lower == self.extracted_title:
            return False
        
        # Basic filters (language-adaptive)
        min_length = 2 if self.detected_language in ['ja', 'zh', 'ko'] else 3
        max_length = 200 if self.detected_language in ['ja', 'zh', 'ko'] else 150
        
        if len(text) < min_length or len(text) > max_length:
            return False
        
        # Universal skip patterns (no content-specific logic)
        skip_patterns = [
            r'^\.+$', r'^\d+\.?\s*$', r'^[a-z]\)?\s*$',
            r'^page \d+', r'^version \d+\.\d+$',
            r'^\d{1,2}/\d{1,2}/\d{4}$', r'^copyright.*\d{4}$',
            r'^www\.', r'^http[s]?://', r'^email:', r'^tel:',
            r'^\d+$', r'^[ivx]+$'
        ]
        
        if any(re.match(pattern, text_lower) for pattern in skip_patterns):
            return False
        
        # Font-based validation (universal)
        size_ratio = block['size'] / body_size if body_size > 0 else 1
        
        # Check for universal heading patterns
        has_structural_pattern = self.is_universal_heading_pattern(text)
        
        # Universal heading scoring system
        heading_score = 0
        
        # Font size criteria
        if size_ratio >= 1.4:
            heading_score += 4
        elif size_ratio >= 1.3:
            heading_score += 3
        elif size_ratio >= 1.2:
            heading_score += 2
        elif size_ratio >= 1.1:
            heading_score += 1
        
        # Bold text bonus
        if block['is_bold']:
            heading_score += 2
        
        # Length appropriateness
        word_count = len(text.split()) if self.detected_language in ['en', 'ar'] else len(text)
        if self.detected_language in ['ja', 'zh', 'ko']:
            # For CJK languages, character count
            if 3 <= word_count <= 30:
                heading_score += 2
            elif 30 < word_count <= 50:
                heading_score += 1
        else:
            # For Latin-based languages, word count
            if 2 <= word_count <= 8:
                heading_score += 2
            elif 8 < word_count <= 15:
                heading_score += 1
        
        # Structural pattern bonus
        if has_structural_pattern:
            heading_score += 3
        
        # Universal formatting patterns (no content)
        if text.isupper() and word_count >= 2:  # ALL CAPS
            heading_score += 1
        elif re.match(r'^[A-Z][a-zA-Z\s\-\'(),]+$', text) and word_count >= 2:  # Title Case
            heading_score += 1
        elif text.endswith(':') and len(text) > 8:  # Ends with colon
            heading_score += 1
        
        # Return true if score meets threshold
        return heading_score >= 4
    
    def get_heading_level(self, block, text):
        """Generic heading level determination"""
        text_normalized = self.normalize_text(text)
        
        # Language-specific structural level detection
        if self.detected_language == "ja":
            if re.search(r'^第[一二三四五六七八九十\d]+章', text_normalized):
                return 1  # Chapter
            elif re.search(r'^第[一二三四五六七八九十\d]+節', text_normalized):
                return 2  # Section
            elif re.search(r'^[一二三四五六七八九十\d]+\.', text_normalized):
                return 3  # Subsection
        
        elif self.detected_language in ["zh", "ko"]:
            if re.search(r'^第[一二三四五六七八九十\d]+[章节]', text_normalized):
                return 1
            elif re.search(r'^[一二三四五六七八九十\d]+\.', text_normalized):
                return 2
        
        elif self.detected_language == "ar":
            if re.search(r'^[٠-٩0-9]+\.', text_normalized):
                return 2
        
        else:
            # Universal Latin patterns
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
            elif text_normalized.endswith(':'):
                return 2  # "Section:"
        
        # Fallback: use font size for level determination
        body_size = max(self.font_stats.items(), key=lambda x: x[1])[0] if self.font_stats else 12.0
        size_ratio = block['size'] / body_size
        
        if size_ratio >= 1.5:
            return 1
        elif size_ratio >= 1.3:
            return 2
        else:
            return 3
    
    def enforce_hierarchy(self, headings):
        """Enforce proper heading hierarchy"""
        if not headings:
            return []
        
        result = []
        current_level = 0
        
        for heading in headings:
            base_level = heading['level']
            
            # First heading - start appropriately
            if current_level == 0:
                final_level = min(base_level, 2)  # Start with H1 or H2
                current_level = final_level
            else:
                # Enforce logical progression
                if base_level <= current_level:
                    final_level = base_level
                    current_level = final_level
                elif base_level == current_level + 1:
                    final_level = base_level
                    current_level = final_level
                else:
                    # Don't jump more than one level
                    final_level = min(current_level + 1, 3)
                    current_level = final_level
            
            # Convert to H1, H2, H3 format
            level_map = {1: 'H1', 2: 'H2', 3: 'H3'}
            
            result.append({
                'level': level_map.get(final_level, 'H3'),
                'text': heading['text'],
                'page': heading['page']
            })
        
        return result
    
    def extract_outline(self, pdf_path):
        """Main extraction method - completely generic"""
        try:
            self.analyze_fonts(pdf_path)
            
            if not self.text_blocks:
                return {"title": "", "outline": []}
            
            # Extract title
            title = self.extract_title()
            
            # Determine body text size
            if not self.font_stats:
                return {"title": title, "outline": []}
            
            body_size = max(self.font_stats.items(), key=lambda x: x[1])[0]
            
            # Extract potential headings
            potential_headings = []
            seen_texts = set()
            
            # Sort blocks by page and position
            sorted_blocks = sorted(self.text_blocks, key=lambda b: (b['page'], -b['y']))
            
            for block in sorted_blocks:
                if self.is_valid_heading(block, body_size):
                    text = block['text'].strip()
                    text = re.sub(r'\s+', ' ', text)
                    text_key = text.lower()
                    
                    # Avoid duplicates
                    min_length = 2 if self.detected_language in ['ja', 'zh', 'ko'] else 3
                    if text_key not in seen_texts and len(text) >= min_length:
                        level = self.get_heading_level(block, text)
                        
                        potential_headings.append({
                            'text': text,
                            'page': block['page'],
                            'level': level,
                            'position': -block['y']
                        })
                        
                        seen_texts.add(text_key)
            
            # Sort by page and position
            potential_headings.sort(key=lambda h: (h['page'], h['position']))
            
            # Enforce hierarchy
            final_outline = self.enforce_hierarchy(potential_headings)
            
            return {
                "title": title,
                "outline": final_outline
            }
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return {"title": "", "outline": []}


def process_all_pdfs():
    """Process all PDFs in input directory and generate JSON outputs"""
    input_dir = Path("input")
    output_dir = Path("output")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize generic extractor
    extractor = GenericOutlineExtractor()
    
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
    print("Starting Generic PDF Outline Extraction...")
    process_all_pdfs()
    print("Processing completed.")
