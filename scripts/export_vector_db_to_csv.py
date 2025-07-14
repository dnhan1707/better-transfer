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

class VectorDBExporter:
    def __init__(self):
        self.rag_database_url = os.getenv("RAG_DATABASE_URL")
        self.engine = create_engine(self.rag_database_url)
        self.export_dir = Path("csv_exports/vector_db")
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
    
    def export_embedding_cache(self):
        """Export embedding_cache table to CSV"""
        print("Exporting embedding_cache table...")
        
        try:
            with self.engine.connect() as conn:
                # Get table info first
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'embedding_cache'
                    ORDER BY ordinal_position
                """))
                
                columns_info = result.fetchall()
                print(f"Found columns: {[col[0] for col in columns_info]}")
                
                # Export data
                result = conn.execute(text("SELECT * FROM embedding_cache"))
                rows = result.fetchall()
                column_names = result.keys()
                
                # Clean column names
                clean_columns = [self.clean_column_name(col) for col in column_names]
                
                print(f"Exporting {len(rows)} rows from embedding_cache...")
                
                # Write to CSV
                csv_path = self.export_dir / "embedding_cache.csv"
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
                
                print(f"✅ Successfully exported embedding_cache to {csv_path}")
                return True
                
        except Exception as e:
            print(f"❌ Error exporting embedding_cache: {e}")
            traceback.print_exc()
            return False
    
    def export_knowledge_chunks_v2(self):
        """Export knowledge_chunks_v2 table to CSV"""
        print("Exporting knowledge_chunks_v2 table...")
        
        try:
            with self.engine.connect() as conn:
                # Get table info first
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'knowledge_chunks_v2'
                    ORDER BY ordinal_position
                """))
                
                columns_info = result.fetchall()
                print(f"Found columns: {[col[0] for col in columns_info]}")
                
                # Export data
                result = conn.execute(text("SELECT * FROM knowledge_chunks_v2"))
                rows = result.fetchall()
                column_names = result.keys()
                
                # Clean column names
                clean_columns = [self.clean_column_name(col) for col in column_names]
                
                print(f"Exporting {len(rows)} rows from knowledge_chunks_v2...")
                
                # Write to CSV
                csv_path = self.export_dir / "knowledge_chunks_v2.csv"
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
                                # Handle vector columns (they might be arrays)
                                formatted_row.append(str(value))
                        writer.writerow(formatted_row)
                
                print(f"✅ Successfully exported knowledge_chunks_v2 to {csv_path}")
                return True
                
        except Exception as e:
            print(f"❌ Error exporting knowledge_chunks_v2: {e}")
            traceback.print_exc()
            return False
    
    def export_all_tables(self):
        """Export all vector database tables"""
        print("=== EXPORTING VECTOR DATABASE TABLES ===\n")
        
        results = {}
        
        # Export embedding_cache
        results['embedding_cache'] = self.export_embedding_cache()
        print()
        
        # Export knowledge_chunks_v2
        results['knowledge_chunks_v2'] = self.export_knowledge_chunks_v2()
        print()
        
        # Summary
        print("=== EXPORT SUMMARY ===")
        for table, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{table}: {status}")
        
        if all(results.values()):
            print(f"\n🎉 All tables exported successfully!")
            print(f"CSV files saved to: {self.export_dir}")
        else:
            print(f"\n⚠️ Some exports failed. Check the logs above.")
    
    def list_all_tables(self):
        """List all tables in the vector database for verification"""
        print("=== VECTOR DATABASE TABLES ===")
        
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
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    row_count = count_result.scalar()
                    
                    print(f"📊 {table_name}: {row_count} rows, {column_count} columns")
                
        except Exception as e:
            print(f"❌ Error listing tables: {e}")

def main():
    """Main function to export vector database tables"""
    print("Vector Database CSV Exporter")
    print("=" * 40)
    
    exporter = VectorDBExporter()
    
    # First, list all available tables
    exporter.list_all_tables()
    print()
    
    # Export the tables
    exporter.export_all_tables()

if __name__ == "__main__":
    main()