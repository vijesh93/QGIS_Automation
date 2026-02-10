import os
import argparse
import psycopg2
from schemas.request import AnalysisRequest # Import our new schema
from qgis.core import QgsApplication, QgsVectorLayer, QgsVectorFileWriter
from export_qgis_shape_file import ExportQGISShape


def run_automation_biotopverbund(raw_year):

    
    # The input is current year, and the querry needs 7 years back, so we need to calculate that and pass it to the SQL query.
    target_year = int(raw_year) - 6  # Ensure it's an integer

    # 1. Validate Input with Pydantic
    try:
        validated_input = AnalysisRequest(target_year=target_year)
        year = validated_input.target_year
    except Exception as e:
        print(f"❌ Input Validation Error: {e}")
        return

    # 2. Database Execution
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            port=os.getenv('DB_PORT')
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Load SQL from the new folder
        sql_path = os.path.join(os.path.dirname(__file__), 'sql', 'Queries_biotopverbund_utm_template_year-dato.sql')
        with open(sql_path, 'r', encoding='utf-8') as f:
            query = f.read()
            # print(f"✅ SQL query: {query}")

        print(f"Executing SQL for year >= {year}...")
        # Safe parameter injection
        cur.execute(query, {'target_year': year})
        print("✅ Database tables updated.")

        # 3. QGIS Export Logic
        # (Assuming the export_to_shapefile logic we discussed previously)
        # export_to_shapefile(year, "fiaka_use", "tbl_view_probestellen_biotop_utm")
        with ExportQGISShape() as exporter:
            # First Layer: Probestellen
            exporter.export_to_shapefile(
                "Auto_Projekt_Biotopverbung_Fiaka-Auszug_probestellen", 
                year + 6,  # We want the filename to reflect the full range, so we add 6 back to show the original input year
                "fiaka_use", 
                "tbl_view_probestellen_biotop_utm"
            )
            
            # Second Layer: Arten (uses same environment, to avoid crash!)
            exporter.export_to_shapefile(
                "Auto_Projekt_Biotopverbung_Fiaka-Auszug_arten", 
                year + 6,  # Same logic for filename
                "fiaka_use", 
                "tbl_view_arten_biotop_utm"
            )

    except Exception as e:
        print(f"❌ Execution Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2019)
    args = parser.parse_args()
    
    run_automation_biotopverbund(args.year)