import itertools
import re
from datetime import datetime
import argparse
import os
import sys
from typing import List, Dict, Optional, Set

class AdvancedPasswordGenerator:
    """
    🔐 Professional Password Wordlist Generator with Special Character Control
    Generates comprehensive password combinations based on personal information
    with configurable special character inclusion and advanced pattern variations.
    """
    
    def __init__(self):
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.number_suffixes = ["", "1", "12", "123", "1234", "12345", "123456", "111", "000", "007", "69", "21"]
        self.year_suffixes = ["", str(datetime.now().year), str(datetime.now().year)[2:], "2020", "2021", "2022", "2023", "2024", "2025"]
        self.leet_replacements = {
            'a': ['4', '@'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7'],
            'b': ['8'],
            'g': ['9']
        }
        self.common_patterns = [
            "qwerty", "qwerty123", "qwertyuiop", "1q2w3e4r", "1qaz2wsx",
            "asdfgh", "zxcvbn", "password", "passw0rd", "admin", "welcome",
            "login", "letmein", "monkey", "dragon", "sunshine", "iloveyou",
            "princess", "football", "baseball", "mustang", "superman"
        ]
    
    def _get_user_choice(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no input from user with default value"""
        while True:
            choice = input(f"{prompt} [{'Y/n' if default else 'y/N'}] ").strip().lower()
            if not choice:
                return default
            if choice in ('y', 'yes'):
                return True
            if choice in ('n', 'no'):
                return False
            print("Please enter 'y' or 'n'")

    def _process_date(self, date_str: str) -> Set[str]:
        """Generate multiple date format variations"""
        variations = set()
        numbers = re.sub(r'[^0-9]', '', date_str)
        
        if not numbers:
            return variations
            
        # Add different date segment combinations
        variations.add(numbers)
        
        if len(numbers) == 8:  # YYYYMMDD
            variations.update([
                numbers[4:],       # MMDD
                numbers[2:],      # YYMMDD
                numbers[4:6],      # MM
                numbers[6:],      # DD
                numbers[2:6],     # YYMM
                numbers[4:6] + numbers[6:]  # MMDD
            ])
        elif len(numbers) == 6:  # YYMMDD or DDMMYY
            variations.update([
                numbers[2:],      # MMDD or MMYY
                numbers[:2],       # YY or DD
                numbers[2:4],      # MM
                numbers[-2:]       # DD or YY
            ])
        elif len(numbers) == 4:  # YYYY or MMDD
            variations.update([numbers[2:], numbers[-2:]])
            
        return variations

    def _generate_leet_variations(self, word: str) -> Set[str]:
        """Generate leet speak variations with progressive replacement"""
        variations = {word}
        
        for i in range(1, 4):  # Multiple levels of leet replacement
            new_variations = set()
            for variant in variations:
                for char in variant.lower():
                    if char in self.leet_replacements:
                        for replacement in self.leet_replacements[char]:
                            new_variations.add(variant.replace(char, replacement))
            variations.update(new_variations)
            
        return variations

    def _generate_case_variations(self, word: str) -> Set[str]:
        """Generate strategic case variations"""
        variations = set()
        if not word:
            return variations
            
        word_lower = word.lower()
        variations.update([
            word_lower,
            word_lower.capitalize(),
            word_lower.upper(),
            word_lower[:-1] + word[-1].upper(),
            word[0].upper() + word_lower[1:]
        ])
        
        # Toggle case for short words
        if len(word) <= 6:
            variations.add(''.join([c.upper() if i%2 else c.lower() for i, c in enumerate(word)]))
            variations.add(''.join([c.lower() if i%2 else c.upper() for i, c in enumerate(word)]))
            
        return variations

    def _generate_combined_patterns(
        self,
        elements: List[str],
        use_special_chars: bool,
        max_length: int = 30
    ) -> Set[str]:
        """Generate advanced password patterns with configurable options"""
        passwords = set()
        clean_elements = [e for e in elements if e]
        
        # Generate combinations of 1-3 elements
        for r in range(1, min(4, len(clean_elements) + 1)):
            for combo in itertools.permutations(clean_elements, r):
                base = ''.join(combo)
                
                # Case variations
                for case_variant in self._generate_case_variations(base):
                    if len(case_variant) > max_length:
                        continue
                        
                    # Number suffixes
                    for num in self.number_suffixes:
                        if len(case_variant + num) > max_length:
                            continue
                        passwords.add(case_variant + num)
                        
                        # Special character suffixes
                        if use_special_chars:
                            for char in self.special_chars:
                                combo = case_variant + num + char
                                if len(combo) <= max_length:
                                    passwords.add(combo)
                    
                    # Year suffixes
                    for year in self.year_suffixes:
                        combo = case_variant + year
                        if len(combo) <= max_length:
                            passwords.add(combo)
                            
                    # Leet variations
                    for leet in self._generate_leet_variations(case_variant):
                        if len(leet) <= max_length:
                            passwords.add(leet)
                            
        # Separator patterns
        if len(clean_elements) >= 2:
            separators = ['', '_', '.', '-'] + (list(self.special_chars) if use_special_chars else [])
            for sep in separators:
                combo = f"{clean_elements[0]}{sep}{clean_elements[1]}"
                if len(combo) <= max_length:
                    passwords.add(combo)
                    
        return passwords

    def generate(
        self,
        personal_info: Dict[str, str],
        use_special_chars: bool = True,
        min_length: int = 6,
        max_length: int = 30
    ) -> List[str]:
        """
        Generate password combinations with professional patterns
        
        Args:
            personal_info: Dictionary containing personal information fields
            use_special_chars: Whether to include special characters
            min_length: Minimum password length to include
            max_length: Maximum password length to allow
            
        Returns:
            List of generated passwords sorted by length
        """
        # Process personal information
        email_local = personal_info.get('email', '').split('@')[0]
        phone_digits = re.sub(r'[^0-9]', '', personal_info.get('phone', ''))
        
        # Collect all base elements
        elements = list({
            personal_info.get('first_name', ''),
            personal_info.get('last_name', ''),
            personal_info.get('nickname', ''),
            email_local,
            *self._process_date(personal_info.get('birth_date', '')),
            *[phone_digits[i:] for i in range(0, len(phone_digits), 2)][:5],  # Phone segments
            personal_info.get('pet_name', ''),
            personal_info.get('spouse_name', ''),
            personal_info.get('favorite_team', ''),
            personal_info.get('favorite_player', ''),
            *personal_info.get('keywords', [])
        })
        
        # Generate password patterns
        passwords = self._generate_combined_patterns(
            elements,
            use_special_chars,
            max_length
        )
        
        # Add common patterns
        passwords.update(self.common_patterns)
        
        # Add year combinations
        for element in elements:
            for year in self.year_suffixes:
                if year:
                    combo = element + year
                    if min_length <= len(combo) <= max_length:
                        passwords.add(combo)
        
        # Filter by length and remove duplicates
        filtered = [p for p in passwords if min_length <= len(p) <= max_length]
        
        # Sort by length then alphabetically
        return sorted(filtered, key=lambda x: (len(x), x))


def collect_personal_info(interactive: bool = False) -> Dict[str, str]:
    """Collect personal information through CLI or defaults"""
    if interactive:
        print("\n🔐 Professional Password Wordlist Generator\n")
        print("ℹ️  Please provide personal information (leave blank if unknown)")
        
        return {
            'first_name': input("👤 First Name: ").strip(),
            'last_name': input("👨‍👩‍👦 Last Name: ").strip(),
            'nickname': input("📛 Nickname: ").strip(),
            'birth_date': input("🎂 Birth Date (any format): ").strip(),
            'email': input("📧 Email: ").strip(),
            'phone': input("📞 Phone (any format): ").strip(),
            'pet_name': input("🐕 Pet's Name: ").strip(),
            'spouse_name': input("💑 Spouse's Name: ").strip(),
            'favorite_team': input("🏈 Favorite Team: ").strip(),
            'favorite_player': input("🏀 Favorite Player: ").strip(),
            'keywords': collect_keywords()
        }
    else:
        return {
            'first_name': 'John',
            'last_name': 'Doe',
            'birth_date': '1990-05-15',
            'email': 'john.doe@example.com',
            'phone': '+1 (555) 123-4567',
            'keywords': ['secret', 'password']
        }


def collect_keywords() -> List[str]:
    """Collect additional keywords interactively"""
    keywords = []
    print("\n🔑 Additional Keywords (press enter when done)")
    while True:
        kw = input(f"Keyword {len(keywords)+1}: ").strip()
        if not kw:
            break
        keywords.append(kw)
    return keywords


def save_wordlist(passwords: List[str], filename: str) -> None:
    """Save passwords to file with checks"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(f"{p}\n" for p in passwords)
        abs_path = os.path.abspath(filename)
        print(f"\n✅ {len(passwords)} passwords generated")
        print(f"💾 Saved to: {abs_path}")
    except IOError as e:
        print(f"\n❌ Error saving file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="🔒 Advanced Password Wordlist Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-o", "--output", help="Output filename", default="wordlist.txt")
    parser.add_argument("--non-interactive", help="Disable interactive mode", action="store_true")
    parser.add_argument("--min-length", help="Minimum password length", type=int, default=6)
    parser.add_argument("--max-length", help="Maximum password length", type=int, default=30)
    args = parser.parse_args()
    
    generator = AdvancedPasswordGenerator()
    
    # Collect information
    personal_info = collect_personal_info(not args.non_interactive)
    
    # Ask about special characters if interactive
    use_special = True
    if not args.non_interactive:
        use_special = generator._get_user_choice("Include special characters?")
    
    # Generate passwords
    passwords = generator.generate(
        personal_info,
        use_special_chars=use_special,
        min_length=args.min_length,
        max_length=args.max_length
    )
    
    # Save results
    save_wordlist(passwords, args.output)


if __name__ == "__main__":
    main()