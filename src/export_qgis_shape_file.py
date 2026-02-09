import os
from qgis.core import (
    QgsApplication, 
    QgsVectorLayer, 
    QgsVectorFileWriter, 
    QgsCoordinateReferenceSystem,
    QgsProject
)


class ExportQGISShape:
    def __init__(self):
        """Initialize the class but don't start QGIS yet."""
        self.qgs = None

    def __enter__(self):
        """Starts QGIS when entering the 'with' block."""
        # The 'False' argument means we run without a GUI (headless)
        self.qgs = QgsApplication([], False)
        self.qgs.initQgis()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleans up and shuts down QGIS when leaving the 'with' block."""
        if self.qgs:
            self.qgs.exitQgis()

    def export_to_shapefile(self, output_file_name, year, schema, table):
        # 1. Logic for naming and directories
        year_int = int(year)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        year_dir = os.path.join(base_dir, f"year_{year_int}", "QGiSLayer")
        
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        output_path = os.path.join(year_dir, f"{output_file_name}_{year_int-6}_{year_int}.shp")
        print(f"--- Exporting {table} to {output_path} ---")

        # 2. Connection Logic (Hidden inside the class)
        uri = (
            f"dbname='{os.getenv('DB_NAME')}' "
            f"host={os.getenv('DB_HOST')} "
            f"port={os.getenv('DB_PORT')} "
            f"user='{os.getenv('DB_USER')}' "
            f"password='{os.getenv('DB_PASS')}' "
            f"key='oid' srid=25832 type=Point checkPrimaryKeyUnicity='0' "
            f"table=\"{schema}\".\"{table}\" (the_geom)"
        )

        vlayer = QgsVectorLayer(uri, f"Layer_{table}", "postgres")

        if not vlayer.isValid():
            print(f"❌ Failed to load PostGIS layer: {table}")
            return

        # 3. Export Logic
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"
        options.destCRS = QgsCoordinateReferenceSystem("EPSG:25832")
        
        # Get context from the project instance
        context = QgsProject.instance().transformContext()

        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            vlayer, 
            output_path, 
            context, 
            options
        )

        if result[0] == QgsVectorFileWriter.NoError:
            print(f"✅ Success: {output_file_name} saved.")
        else:
            print(f"❌ Error: {result[1]}")


class ExportQGISShape_2():
    def export_to_shapefile(self, output_file_name, year, schema, table):
        print(f"--- Exporting Layer to Shapefile for Year {year} ---")
        
        # 1. Setup Folder Structure: data/year_<year>/QGiSLayer/
        # We go up one level from 'src' to find 'data'
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        year_dir = os.path.join(base_dir, f"year_{year}", "QGiSLayer")
        
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
            print(f"Created directory: {year_dir}")
        
        # Finding the year range for the filename
        year_int = int(year) 
        year_minus_6 = year_int - 6  # We want the range to be 7 years back, so we subtract 6 to include the target year
        file_name = f"{output_file_name}_{year_minus_6}_{year_int}.shp"
        output_path = os.path.join(year_dir, file_name)

        # 2. Initialize QGIS (Headless)
        qgs = QgsApplication([], False)
        qgs.initQgis()

        # 3. Define the PostGIS Connection String
        uri = (
            f"dbname='{os.getenv('DB_NAME')}' "
            f"host={os.getenv('DB_HOST')} "
            f"port={os.getenv('DB_PORT')} "
            f"user='{os.getenv('DB_USER')}' "
            f"password='{os.getenv('DB_PASS')}' "
            f"key='oid' srid=25832 type=Point checkPrimaryKeyUnicity='0' "
            f"table=\"{schema}\".\"{table}\" (the_geom)"
        )

        # 4. Load the layer from PostGIS
        vlayer = QgsVectorLayer(uri, f"Layer_{year}", "postgres")

        if not vlayer.isValid():
            print(f"❌ Failed to load PostGIS layer! Check URI/Permissions.")
        else:
            # 5. Export to Shapefile
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"
            options.fileEncoding = "UTF-8"
            
            # WICHTIG: Das Ziel-CRS wird direkt in den Options gesetzt
            options.destCRS = QgsCoordinateReferenceSystem("EPSG:25832")
            
            # WICHTIG: Wir holen uns den Transformations-Kontext vom Projekt-Objekt
            from qgis.core import QgsProject
            context = QgsProject.instance().transformContext()

            # writeAsVectorFormatV3 liefert ein Tupel (Error-Code, Error-Nachricht, Pfad)
            result = QgsVectorFileWriter.writeAsVectorFormatV3(
                vlayer, 
                output_path, 
                context, 
                options
            )

            if result[0] == QgsVectorFileWriter.NoError:
                print(f"✅ Success! Layer dumped to: {output_path}")
            else:
                # result[1] enthält die detaillierte Fehlermeldung von QGIS
                print(f"❌ Error exporting: {result[1]}")

        qgs.exitQgis()

    # Update execute_automation to call this at the end