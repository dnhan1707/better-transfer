import os
import sys
import csv
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class MainDBExporter:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.database_url)
        self.export_dir = Path("csv_exports/main_db")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
    def clean_column_name(self, column_name):
        """Clean column names to remove special characters except - and _"""
        # Replace spaces and other special chars with underscores
        cleaned = column_name.replace(' ', '_')
        # Remove all special characters except hyphens and underscores
        allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
        cleaned = ''.join(c if c in allowed_chars else '_' for c in cleaned)
        return cleaned
    
    def format_datetime(self, value):
        """Format datetime values as YYYY-MM-DD HH:mm:ss"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        # If it's already a string, try to parse and reformat
        if isinstance(value, str):
            try:
                dt = pd.to_datetime(value)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                return value
        return str(value)
    
    def export_table(self, table_name):
        """Export a specific table to CSV"""
        print(f"Exporting {table_name} table...")
        
        try:
            with self.engine.connect() as conn:
                # Get table info first
                result = conn.execute(text(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """))
                
                columns_info = result.fetchall()
                print(f"Found columns: {[col[0] for col in columns_info]}")
                
                # Export data with ORDER BY id if id column exists
                try:
                    result = conn.execute(text(f"SELECT * FROM {table_name} ORDER BY id"))
                except:
                    # If no id column, just select all
                    result = conn.execute(text(f"SELECT * FROM {table_name}"))
                
                rows = result.fetchall()
                column_names = result.keys()
                
                # Clean column names
                clean_columns = [self.clean_column_name(col) for col in column_names]
                
                print(f"Exporting {len(rows)} rows from {table_name}...")
                
                # Write to CSV
                csv_path = self.export_dir / f"{table_name}.csv"
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers
                    writer.writerow(clean_columns)
                    
                    # Write data rows
                    for row in rows:
                        formatted_row = []
                        for value in row:
                            if isinstance(value, datetime):
                                formatted_row.append(self.format_datetime(value))
                            elif value is None:
                                formatted_row.append('')
                            else:
                                formatted_row.append(str(value))
                        writer.writerow(formatted_row)
                
                print(f"✅ Successfully exported {table_name} to {csv_path}")
                return True
                
        except Exception as e:
            print(f"❌ Error exporting {table_name}: {e}")
            traceback.print_exc()
            return False
    
    def export_universities(self):
        """Export universities table to CSV"""
        return self.export_table('universities')
    
    def export_colleges(self):
        """Export colleges table to CSV"""
        return self.export_table('colleges')
    
    def export_majors(self):
        """Export majors table to CSV"""
        return self.export_table('majors')
    
    def export_all_main_tables(self):
        """Export all main database tables"""
        print("=== EXPORTING MAIN DATABASE TABLES ===\n")
        
        # Fixed: Changed 'courses' to 'colleges'
        tables = ['universities', 'colleges', 'majors']
        results = {}
        
        for table in tables:
            results[table] = self.export_table(table)
            print()
        
        # Summary
        print("=== EXPORT SUMMARY ===")
        for table, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{table}: {status}")
        
        if all(results.values()):
            print(f"\n🎉 All main tables exported successfully!")
            print(f"CSV files saved to: {self.export_dir}")
        else:
            print(f"\n⚠️ Some exports failed. Check the logs above.")
    
    def list_all_tables(self):
        """List all tables in the main database for verification"""
        print("=== MAIN DATABASE TABLES ===")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name, 
                           (SELECT COUNT(*) FROM information_schema.columns 
                            WHERE table_name = t.table_name) as column_count
                    FROM information_schema.tables t
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """))
                
                tables = result.fetchall()
                
                for table_name, column_count in tables:
                    # Get row count
                    try:
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        row_count = count_result.scalar()
                        print(f"📊 {table_name}: {row_count} rows, {column_count} columns")
                    except Exception as e:
                        print(f"📊 {table_name}: Error getting row count - {e}")
                
        except Exception as e:
            print(f"❌ Error listing tables: {e}")

def main():
    """Main function to export main database tables"""
    print("Main Database CSV Exporter")
    print("=" * 40)
    
    exporter = MainDBExporter()
    
    # First, list all available tables
    exporter.list_all_tables()
    print()
    
    # Export specific tables
    exporter.export_all_main_tables()

if __name__ == "__main__":
    main()