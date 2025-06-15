#!/usr/bin/env python3
"""
Fix Corrupted Vision Analysis JSON Files
Repairs truncated JSON files in the data/conversations directory
"""

import os
import json
import shutil
from datetime import datetime

def fix_corrupted_json_file(file_path):
    """Fix a single corrupted JSON file"""
    print(f"Fixing: {file_path}")
    
    # Backup original file
    backup_path = f"{file_path}.backup"
    shutil.copy2(file_path, backup_path)
    print(f"  ✅ Created backup: {backup_path}")
    
    try:
        # Read the corrupted file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it ends with incomplete "is_blurry": 
        if content.rstrip().endswith('"is_blurry":'):
            # Complete the JSON structure based on the pattern
            # Determine blur status from blur_score if available
            is_blurry = "false"  # Default to false for good quality
            
            # Try to extract blur_score to determine actual value
            if '"blur_score":' in content:
                try:
                    # Extract blur score value
                    blur_line = [line for line in content.split('\n') if '"blur_score":' in line][0]
                    blur_value = float(blur_line.split(':')[1].replace(',', '').strip())
                    is_blurry = "true" if blur_value < 100 else "false"
                except:
                    is_blurry = "false"
            
            # Complete the JSON structure
            fixed_content = content.rstrip() + f' {is_blurry},\n'
            fixed_content += '      "image_size": "unknown",\n'
            fixed_content += '      "file_size": 0\n'
            fixed_content += '    }\n'
            fixed_content += '  }\n'
            fixed_content += '}'
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # Validate the fixed JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"  ✅ Successfully fixed and validated: {file_path}")
                return True
            except json.JSONDecodeError as e:
                print(f"  ❌ Fixed file still invalid: {e}")
                # Restore backup
                shutil.copy2(backup_path, file_path)
                return False
        
        else:
            print(f"  ℹ️  File doesn't match expected corruption pattern, skipping")
            # Remove unnecessary backup
            os.remove(backup_path)
            return True
            
    except Exception as e:
        print(f"  ❌ Error processing file: {e}")
        # Restore backup if it exists
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        return False

def main():
    """Main function to fix all corrupted vision analysis JSON files"""
    print("🔧 Vision Analysis JSON Repair Tool")
    print("=" * 50)
    
    # Find all vision analysis JSON files
    data_dir = "/home/silentcodinglegendkali/scl-llamaapi/data/conversations"
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    vision_files = [f for f in os.listdir(data_dir) if f.startswith('vision_') and f.endswith('.json')]
    
    if not vision_files:
        print("ℹ️  No vision analysis JSON files found")
        return
    
    print(f"📁 Found {len(vision_files)} vision analysis files")
    print()
    
    # Process each file
    fixed_count = 0
    error_count = 0
    
    for filename in sorted(vision_files):
        file_path = os.path.join(data_dir, filename)
        
        try:
            # First, try to load the file to see if it's corrupted
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            print(f"✅ {filename} - Already valid")
        except json.JSONDecodeError:
            # File is corrupted, attempt to fix it
            if fix_corrupted_json_file(file_path):
                fixed_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"❌ {filename} - Error reading file: {e}")
            error_count += 1
    
    # Summary
    print()
    print("📊 Repair Summary:")
    print(f"   ✅ Successfully fixed: {fixed_count}")
    print(f"   ❌ Errors encountered: {error_count}")
    print(f"   📁 Total files processed: {len(vision_files)}")
    
    if fixed_count > 0:
        print()
        print("🎉 JSON repair completed!")
        print("💡 Backup files (.backup) have been created for safety")
    
if __name__ == "__main__":
    main()
