import itertools
import re
from datetime import datetime
import argparse
import os
from typing import List, Dict, Optional

class PasswordGenerator:
    """
    Advanced password generator that creates comprehensive wordlists based on personal information
    and common password patterns with enhanced security research.
    """
    
    def __init__(self):
        self.common_special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.common_number_suffixes = ["", "123", "1234", "12345", "123456", "1", "12", "111", "000", "007", "69", "21"]
        self.common_year_suffixes = ["", str(datetime.now().year), str(datetime.now().year)[2:], "2020", "2021", "2022", "2023", "2024", "2025"]
        self.common_leet_replacements = {
            'a': ['4', '@'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7'],
            'b': ['8'],
            'g': ['9']
        }
    
    def _process_date(self, date_str: str) -> List[str]:
        """Process birth date into multiple formats"""
        date_variations = set()
        
        if not date_str:
            return []
            
        # Extract pure numbers
        numbers = re.sub(r'[^0-9]', '', date_str)
        if numbers:
            date_variations.add(numbers)
            
            # Add common date formats
            if len(numbers) == 8:  # YYYYMMDD
                date_variations.update([
                    numbers,                           # 19991230
                    numbers[4:],                       # 1230 (MMDD)
                    numbers[2:],                       # 991230 (YYMMDD)
                    numbers[4:6] + numbers[6:],        # 1230 (MMDD)
                    numbers[2:6],                     # 9912 (YYMM)
                    numbers[-2:],                     # 30 (DD)
                ])
            elif len(numbers) == 6:  # YYMMDD or DDMMYY
                date_variations.update([
                    numbers,                           # 991230
                    numbers[2:],                       # 1230 (MMDD)
                    numbers[:2] + numbers[2:4],        # 9912 (YYMM)
                    numbers[-2:],                     # 30 (DD)
                ])
            elif len(numbers) == 4:  # YYYY or MMDD
                date_variations.update([
                    numbers,                           # 1999 or 1230
                    numbers[2:],                       # 99 (YY)
                    numbers[-2:],                      # 99 or 30
                ])
        
        return list(date_variations)
    
    def _generate_leet_variations(self, word: str) -> List[str]:
        """Generate leet speak variations of a word"""
        variations = [word]
        
        for char in word.lower():
            if char in self.common_leet_replacements:
                new_variations = []
                for replacement in self.common_leet_replacements[char]:
                    for variant in variations:
                        new_variations.append(variant.replace(char, replacement))
                variations += new_variations
                
        return list(set(variations))  # Remove duplicates
    
    def _generate_case_variations(self, word: str) -> List[str]:
        """Generate different case variations of a word"""
        if not word:
            return []
            
        variations = set()
        word_lower = word.lower()
        
        # Common case patterns
        variations.update([
            word_lower,                        # lowercase
            word_lower.capitalize(),            # Capitalized
            word_lower.upper(),                 # UPPERCASE
        ])
        
        # Toggle case patterns
        if len(word) > 1:
            variations.add(word_lower[:-1] + word[-1].upper())  # last letter uppercase
            variations.add(word[0].upper() + word_lower[1:])    # first letter uppercase
            
        return list(variations)
    
    def _generate_common_patterns(self, elements: List[str]) -> List[str]:
        """Generate passwords using common patterns"""
        passwords = set()
        elements = [e for e in elements if e]  # Remove empty elements
        
        # Generate all combinations of 1-4 elements
        for r in range(1, min(5, len(elements) + 1)):
            for combination in itertools.permutations(elements, r):
                base = ''.join(combination)
                
                # Generate case variations
                for case_variant in self._generate_case_variations(base):
                    # Add number suffixes
                    for num_suffix in self.common_number_suffixes:
                        passwords.add(f"{case_variant}{num_suffix}")
                    
                    # Add year suffixes
                    for year_suffix in self.common_year_suffixes:
                        passwords.add(f"{case_variant}{year_suffix}")
                    
                    # Add special character suffixes
                    for char in self.common_special_chars:
                        passwords.add(f"{case_variant}{char}")
                    
                    # Add both number and special
                    for num_suffix in self.common_number_suffixes:
                        for char in self.common_special_chars:
                            passwords.add(f"{case_variant}{num_suffix}{char}")
                
                # Generate leet variations
                for leet_variant in self._generate_leet_variations(base):
                    passwords.add(leet_variant)
                    
                    # Add number suffixes to leet variants
                    for num_suffix in self.common_number_suffixes:
                        passwords.add(f"{leet_variant}{num_suffix}")
        
        # Common separator patterns
        if len(elements) >= 2:
            for sep in ['', '.', '_', '-', '@', '!', '#', '$', '%']:
                passwords.add(f"{elements[0]}{sep}{elements[1]}")
                if len(elements) >= 3:
                    passwords.add(f"{elements[0]}{sep}{elements[1]}{sep}{elements[2]}")
        
        return list(passwords)
    
    def generate_passwords(
        self,
        first_name: str,
        last_name: str,
        birth_date: str,
        email: str,
        phone: str,
        nickname: str = "",
        pet_name: str = "",
        spouse_name: str = "",
        favorite_team: str = "",
        favorite_player: str = "",
        keywords: List[str] = None
    ) -> List[str]:
        """
        Generate password guesses based on personal information and advanced patterns.
        
        Args:
            first_name: First name
            last_name: Last name
            birth_date: Birth date in any format
            email: Email address
            phone: Phone number
            nickname: Nickname (optional)
            pet_name: Pet's name (optional)
            spouse_name: Spouse's name (optional)
            favorite_team: Favorite sports team (optional)
            favorite_player: Favorite player (optional)
            keywords: Additional keywords (optional)
            
        Returns:
            List of generated passwords
        """
        if keywords is None:
            keywords = []
            
        # Process email
        email_local = email.split('@')[0] if email else ""
        
        # Process phone
        phone_digits = re.sub(r'[^0-9]', '', phone) if phone else ""
        phone_variations = set()
        if phone_digits:
            phone_variations.add(phone_digits)
            if len(phone_digits) == 10:
                phone_variations.update([
                    phone_digits[-4:],          # last 4 digits
                    phone_digits[-6:],          # last 6 digits
                    phone_digits[:3],           # area code
                    phone_digits[3:6],          # exchange code
                ])
            elif len(phone_digits) > 4:
                phone_variations.add(phone_digits[-4:])
        
        # Process date variations
        date_variations = self._process_date(birth_date)
        
        # Collect all elements
        elements = list(set([
            first_name, last_name, nickname, email_local,
            *date_variations, *phone_variations, pet_name,
            spouse_name, favorite_team, favorite_player, *keywords
        ]))
        
        # Remove empty elements and duplicates
        elements = [e for e in elements if e]
        
        # Generate passwords
        passwords = self._generate_common_patterns(elements)
        
        # Add concatenated year variations
        for element in elements:
            for year in self.common_year_suffixes:
                if year:
                    passwords.append(f"{element}{year}")
        
        # Add common keyboard patterns
        common_keyboard_patterns = [
            "qwerty", "qwerty123", "qwertyuiop", "1q2w3e4r", "1qaz2wsx",
            "asdfgh", "zxcvbn", "password", "passw0rd", "admin", "welcome",
            "login", "letmein", "monkey", "dragon", "sunshine", "iloveyou",
            "princess", "football", "baseball", "mustang", "superman"
        ]
        passwords.extend(common_keyboard_patterns)
        
        # Filter out too short passwords (min 6 chars)
        passwords = [p for p in passwords if len(p) >= 6]
        
        # Remove duplicates
        return list(set(passwords))


def main():
    parser = argparse.ArgumentParser(description="🔐 Advanced Password Wordlist Generator")
    parser.add_argument("-o", "--output", help="Output file name", default="wordlist.txt")
    parser.add_argument("-q", "--quiet", help="Quiet mode (no interactive input)", action="store_true")
    
    args = parser.parse_args()
    
    generator = PasswordGenerator()
    
    if not args.quiet:
        print("\n🔐 Advanced Password Wordlist Generator\n")
        print("ℹ️  Please provide personal information (leave blank if unknown)")
        
        first_name = input("👤 First Name: ").strip()
        last_name = input("👨‍👩‍👦 Last Name: ").strip()
        nickname = input("📛 Nickname (optional): ").strip()
        birth_date = input("🎂 Birth Date (any format): ").strip()
        email = input("📧 Email Address: ").strip()
        phone = input("📞 Phone Number (any format): ").strip()
        pet_name = input("🐕 Pet's Name (optional): ").strip()
        spouse_name = input("💑 Spouse's Name (optional): ").strip()
        favorite_team = input("🏈 Favorite Team (optional): ").strip()
        favorite_player = input("🏀 Favorite Player (optional): ").strip()
        
        keywords = []
        while True:
            keyword = input("🔑 Additional Keyword (or press enter to finish): ").strip()
            if not keyword:
                break
            keywords.append(keyword)
        
        passwords = generator.generate_passwords(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            email=email,
            phone=phone,
            nickname=nickname,
            pet_name=pet_name,
            spouse_name=spouse_name,
            favorite_team=favorite_team,
            favorite_player=favorite_player,
            keywords=keywords
        )
    else:
        # Example usage for non-interactive mode
        passwords = generator.generate_passwords(
            first_name="John",
            last_name="Doe",
            birth_date="1990-05-15",
            email="john.doe@example.com",
            phone="+1 (555) 123-4567",
            nickname="johny",
            pet_name="Max",
            keywords=["secret", "password"]
        )
    
    # Save to file
    with open(args.output, "w", encoding="utf-8") as f:
        for pwd in passwords:
            f.write(pwd + "\n")
    
    if not args.quiet:
        print(f"\n✅ {len(passwords)} passwords have been generated.")
        print(f"📁 Saved to: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()