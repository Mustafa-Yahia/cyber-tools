import re
import mmap
from collections import defaultdict
import heapq
import os
import time
from tqdm import tqdm

class AdvancedPasswordFilter:
    def __init__(self):
        # تحميل قوائم الكلمات الشائعة وأنماط كلمات المرور الضعيفة
        self.common_passwords = self._load_common_passwords()
        self.weak_patterns = self._load_weak_patterns()
        
    def _load_common_passwords(self, top_n=10000):
        """تحميل القائمة الأكثر شيوعاً لكلمات المرور"""
        common = set()
        try:
            with open('top-passwords.txt', 'r', encoding='utf-8', errors='ignore') as f:
                for line in itertools.islice(f, top_n):
                    common.add(line.strip().lower())
        except FileNotFoundError:
            # قائمة افتراضية إذا لم يوجد ملف
            common.update(['123456', 'password', '123456789', '12345', 'qwerty'])
        return common
    
    def _load_weak_patterns(self):
        """تحميل أنماط كلمات المرور الضعيفة"""
        patterns = {
            'numeric_sequence': r'12345678?9?0?',
            'reverse_numeric': r'98765432?1?0?',
            'keyboard_patterns': [
                r'qwertyuiop', r'asdfghjkl', r'zxcvbnm',
                r'1qaz2wsx', r'1q2w3e4r', r'123qwe'
            ],
            'repeated_chars': r'(\w)\1{2,}',
            'short_passwords': r'^.{1,7}$'
        }
        return patterns
    
    def _matches_weak_pattern(self, password):
        """فحص إذا كانت كلمة المرور تطابق أنماطاً ضعيفة"""
        # التحقق من الأنماط الرقمية
        if re.search(self.weak_patterns['numeric_sequence'], password):
            return True
        if re.search(self.weak_patterns['reverse_numeric'], password):
            return True
            
        # التحقق من أنماط لوحة المفاتيح
        for pattern in self.weak_patterns['keyboard_patterns']:
            if re.search(pattern, password.lower()):
                return True
                
        # التحقق من الأحرف المتكررة
        if re.search(self.weak_patterns['repeated_chars'], password):
            return True
            
        # التحقق من كلمات المرور القصيرة جداً
        if re.search(self.weak_patterns['short_passwords'], password):
            return True
            
        return False
    
    def filter_large_file(self, input_file, output_file, filters):
        """
        تصفية ملف كبير من كلمات المرور مع دعم الذاكرة الفعالة
        
        المعايير المتاحة:
        - min_length: الحد الأدنى لطول كلمة المرور
        - max_length: الحد الأقصى لطول كلمة المرور
        - require_upper: تتطلب حرف كبير على الأقل
        - require_lower: تتطلب حرف صغير على الأقل
        - require_digit: تتطلب رقم على الأقل
        - require_special: تتطلب رمز خاص على الأقل
        - exclude_common: استبعاد كلمات المرور الشائعة
        - exclude_weak_patterns: استبعاد الأنماط الضعيفة
        - custom_regex: تعبير نمطي مخصص للاستبعاد
        - keep_unique: الاحتفاظ بالكلمات الفريدة فقط
        """
        start_time = time.time()
        unique_passwords = set() if filters.get('keep_unique', False) else None
        total_count = 0
        filtered_count = 0
        
        # حساب عدد الأسطر للملف (لشريط التقدم)
        file_size = os.path.getsize(input_file)
        
        with open(input_file, 'r+', encoding='utf-8', errors='ignore') as infile:
            # استخدام mmap لمعالجة الملف الكبير بكفاءة
            mm = mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ)
            
            with open(output_file, 'w', encoding='utf-8') as outfile:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc="معالجة الملف") as pbar:
                    for line in iter(mm.readline, b''):
                        try:
                            password = line.decode('utf-8').strip()
                        except UnicodeDecodeError:
                            password = line.decode('latin-1').strip()
                            
                        total_count += 1
                        pbar.update(len(line))
                        
                        # تطبيق الفلاتر
                        include = True
                        
                        if 'min_length' in filters and len(password) < filters['min_length']:
                            include = False
                        if 'max_length' in filters and len(password) > filters['max_length']:
                            include = False
                        if 'require_upper' in filters and not re.search(r'[A-Z]', password):
                            include = False
                        if 'require_lower' in filters and not re.search(r'[a-z]', password):
                            include = False
                        if 'require_digit' in filters and not re.search(r'[0-9]', password):
                            include = False
                        if 'require_special' in filters and not re.search(r'[^A-Za-z0-9]', password):
                            include = False
                        if 'exclude_common' in filters and password.lower() in self.common_passwords:
                            include = False
                        if 'exclude_weak_patterns' in filters and self._matches_weak_pattern(password):
                            include = False
                        if 'custom_regex' in filters and re.search(filters['custom_regex'], password):
                            include = False
                            
                        if include:
                            if unique_passwords is not None:
                                if password not in unique_passwords:
                                    unique_passwords.add(password)
                                    outfile.write(password + '\n')
                                    filtered_count += 1
                            else:
                                outfile.write(password + '\n')
                                filtered_count += 1
                                
        elapsed_time = time.time() - start_time
        stats = {
            'total_passwords': total_count,
            'filtered_passwords': filtered_count,
            'filtered_percentage': (filtered_count / total_count) * 100 if total_count > 0 else 0,
            'time_elapsed': elapsed_time,
            'passwords_per_second': total_count / elapsed_time if elapsed_time > 0 else 0
        }
        
        return stats
    
    def analyze_file(self, input_file):
        """تحليل ملف كلمات المرور وإنتاج إحصاءات"""
        stats = {
            'length_dist': defaultdict(int),
            'composition': defaultdict(int),
            'common_count': 0,
            'weak_pattern_count': 0,
            'total': 0
        }
        
        file_size = os.path.getsize(input_file)
        
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="تحليل الملف") as pbar:
                for line in f:
                    password = line.strip()
                    stats['total'] += 1
                    pbar.update(len(line.encode('utf-8')))
                    
                    # تحليل الطول
                    length = len(password)
                    stats['length_dist'][length] += 1
                    
                    # تحليل التركيبة
                    has_upper = re.search(r'[A-Z]', password)
                    has_lower = re.search(r'[a-z]', password)
                    has_digit = re.search(r'[0-9]', password)
                    has_special = re.search(r'[^A-Za-z0-9]', password)
                    
                    if has_upper and has_lower and has_digit and has_special:
                        stats['composition']['mixed_all'] += 1
                    elif has_upper and has_lower and has_digit:
                        stats['composition']['mixed_alpha_num'] += 1
                    elif has_upper and has_lower:
                        stats['composition']['mixed_alpha'] += 1
                    elif has_lower and has_digit:
                        stats['composition']['lower_num'] += 1
                    elif has_lower:
                        stats['composition']['lower_only'] += 1
                    elif has_upper:
                        stats['composition']['upper_only'] += 1
                    elif has_digit:
                        stats['composition']['numbers_only'] += 1
                    else:
                        stats['composition']['special_only'] += 1
                    
                    # التحقق من كلمات المرور الشائعة
                    if password.lower() in self.common_passwords:
                        stats['common_count'] += 1
                        
                    # التحقق من الأنماط الضعيفة
                    if self._matches_weak_pattern(password):
                        stats['weak_pattern_count'] += 1
        
        return stats
    
    def split_large_file(self, input_file, output_prefix, chunk_size=1000000):
        """تقسيم ملف كبير إلى أجزاء أصغر"""
        file_count = 0
        line_count = 0
        
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
            outfile = None
            
            for line in tqdm(infile, desc="تقسيم الملف"):
                if line_count % chunk_size == 0:
                    if outfile is not None:
                        outfile.close()
                    file_count += 1
                    outfile = open(f"{output_prefix}_{file_count}.txt", 'w', encoding='utf-8')
                
                outfile.write(line)
                line_count += 1
            
            if outfile is not None:
                outfile.close()
        
        return file_count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="أداة متقدمة لفلترة قوائم كلمات المرور الكبيرة")
    parser.add_argument("input_file", help="ملف كلمات المرور المدخلة")
    parser.add_argument("-o", "--output", help="ملف الإخراج للكلمات المصفاة", required=True)
    parser.add_argument("--min_length", type=int, help="الحد الأدنى لطول كلمة المرور")
    parser.add_argument("--max_length", type=int, help="الحد الأقصى لطول كلمة المرور")
    parser.add_argument("--require_upper", action="store_true", help="تتطلب حرف كبير على الأقل")
    parser.add_argument("--require_lower", action="store_true", help="تتطلب حرف صغير على الأقل")
    parser.add_argument("--require_digit", action="store_true", help="تتطلب رقم على الأقل")
    parser.add_argument("--require_special", action="store_true", help="تتطلب رمز خاص على الأقل")
    parser.add_argument("--exclude_common", action="store_true", help="استبعاد كلمات المرور الشائعة")
    parser.add_argument("--exclude_weak_patterns", action="store_true", help="استبعاد الأنماط الضعيفة")
    parser.add_argument("--custom_regex", help="تعبير نمطي مخصص للاستبعاد")
    parser.add_argument("--keep_unique", action="store_true", help="الاحتفاظ بالكلمات الفريدة فقط")
    parser.add_argument("--analyze_only", action="store_true", help="إجراء التحليل فقط دون التصفية")
    parser.add_argument("--split", type=int, help="تقسيم الملف إلى أجزاء بحجم معين (عدد الأسطر)")
    
    args = parser.parse_args()
    
    filter_tool = AdvancedPasswordFilter()
    
    if args.split:
        print(f"جاري تقسيم الملف إلى أجزاء بحجم {args.split} سطر...")
        num_files = filter_tool.split_large_file(args.input_file, args.output, args.split)
        print(f"تم تقسيم الملف إلى {num_files} أجزاء")
        return
    
    if args.analyze_only:
        print("جاري تحليل ملف كلمات المرور...")
        stats = filter_tool.analyze_file(args.input_file)
        
        print("\nنتائج التحليل:")
        print(f"إجمالي كلمات المرور: {stats['total']}")
        print(f"كلمات مرور شائعة: {stats['common_count']} ({stats['common_count']/stats['total']:.2%})")
        print(f"كلمات مرور ضعيفة الأنماط: {stats['weak_pattern_count']} ({stats['weak_pattern_count']/stats['total']:.2%})")
        
        print("\nتوزيع الأطوال:")
        for length, count in sorted(stats['length_dist'].items()):
            print(f"- طول {length}: {count} ({count/stats['total']:.2%})")
        
        print("\nتركيبة كلمات المرور:")
        for comp_type, count in stats['composition'].items():
            print(f"- {comp_type}: {count} ({count/stats['total']:.2%})")
        
        return
    
    filters = {}
    if args.min_length:
        filters['min_length'] = args.min_length
    if args.max_length:
        filters['max_length'] = args.max_length
    if args.require_upper:
        filters['require_upper'] = True
    if args.require_lower:
        filters['require_lower'] = True
    if args.require_digit:
        filters['require_digit'] = True
    if args.require_special:
        filters['require_special'] = True
    if args.exclude_common:
        filters['exclude_common'] = True
    if args.exclude_weak_patterns:
        filters['exclude_weak_patterns'] = True
    if args.custom_regex:
        filters['custom_regex'] = args.custom_regex
    if args.keep_unique:
        filters['keep_unique'] = True
    
    print("جاري تصفية كلمات المرور...")
    stats = filter_tool.filter_large_file(args.input_file, args.output, filters)
    
    print("\nنتائج التصفية:")
    print(f"إجمالي كلمات المرور المدخلة: {stats['total_passwords']}")
    print(f"عدد كلمات المرور المصفاة: {stats['filtered_passwords']} ({stats['filtered_percentage']:.2f}%)")
    print(f"الوقت المستغرق: {stats['time_elapsed']:.2f} ثانية")
    print(f"معدل المعالجة: {stats['passwords_per_second']:,.0f} كلمة/ثانية")


if __name__ == "__main__":
    main()