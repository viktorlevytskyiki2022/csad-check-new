import csv
import requests
import os

# --- НАЛАШТУВАННЯ ---
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'

def find_column_by_keyword(fieldnames, keywords):
    if not fieldnames: return None
    for col in fieldnames:
        clean_col = str(col).lower().strip()
        for kw in keywords:
            if kw.lower() in clean_col:
                return col
    return None

def check_repo_exists(username, repo_name):
    if not username or not repo_name: return "EMPTY"
    username, repo_name = username.strip(), repo_name.strip()
    url = f"https://github.com/{username}/{repo_name}"
    try:
        response = requests.get(url, timeout=5)
        return "OK" if response.status_code == 200 else "FAIL"
    except:
        return "ERROR"

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(INPUT_DIR): 
        print("Folder 'input' not found yet. Waiting for Google Sheets...")
        return

    csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
    
    for filename in csv_files:
        print(f"\n📄 Processing: {filename}")
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(input_path, mode='r', encoding='utf-8') as infile:
            clean_lines = (line.replace('\0','') for line in infile)
            reader = csv.DictReader(clean_lines)
            fieldnames = reader.fieldnames
            
            # Шукаємо колонки (Git User та Repo/Group)
            git_col = find_column_by_keyword(fieldnames, ['git name', 'git', 'github'])
            # Шукаємо колонку з 3 цифр (група) або слово repo
            repo_col = None
            for col in fieldnames:
                if str(col).strip().isdigit() and len(str(col).strip()) == 3:
                    repo_col = col; break
            if not repo_col: repo_col = find_column_by_keyword(fieldnames, ['repo', 'repository'])

            print(f"   🎯 Git Column: {git_col} | Repo Column: {repo_col}")
            
            if not repo_col: continue

            fieldnames = fieldnames + ['Status']
            rows_to_write = []
            
            for row in reader:
                git_user = str(row.get(git_col, '') or '').strip()
                repo_name = str(row.get(repo_col, '') or '').strip()
                
                status = "EMPTY"
                if len(git_user) > 1 and len(repo_name) > 1:
                    status = check_repo_exists(git_user, repo_name)
                    print(f"   👉 {git_user}/{repo_name} -> {status}")
                
                row['Status'] = status
                rows_to_write.append(row)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)

if __name__ == "__main__":
    main()
