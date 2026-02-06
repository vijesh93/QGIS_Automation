# NOT IMPLEMENTED YET:

import os
from qgis.core import (
    QgsApplication, 
    QgsProject, 
    QgsVectorLayer, 
    QgsDataSourceUri
)


def read_sql_file(file_path):
    """Reads a .sql file and returns the string content."""
    try:
        with open(file_path, 'r') as f:
            # We strip whitespace and remove the trailing semicolon 
            # because QGIS wraps the query internally
            return f.read().strip().rstrip(';')
    except Exception as e:
        print(f"❌ Error reading SQL file: {e}")
        return None
    

# 1. Initialize QGIS in headless mode
qgs = QgsApplication([], False)
qgs.initQgis()

# 2. Get DB info from Env
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_port = os.getenv('DB_PORT')

# 3. Define the PostGIS connection
uri = QgsDataSourceUri()
uri.setConnection(db_host, db_port, db_name, db_user, db_pass)

# Instead of just a table, you can pass your SQL query here!
# For example: (SELECT * FROM my_table WHERE year = 2026)
if query_content:
    uri = QgsDataSourceUri()
    uri.setConnection(db_host, db_port, db_name, db_user, db_pass)
    
    # In QGIS, for a SQL query (rather than a table), 
    # we pass the query in parentheses as the table name.
    # Logic: (SELECT ...)
    sql_wrapped = f"({query_content})"
    uri.setDataSource("", sql_query, "geom", "", "id_column")

    # 4. Create the layer
    layer = QgsVectorLayer(uri.uri(), "Yearly_Update_Layer", "postgres")

    if not layer.isValid():
        print("❌ Layer failed to load! Check your SQL or URI.")
    else:
        # 5. Load project and add layer
        project = QgsProject.instance()
        project.addMapLayer(layer)
        
        # Save to the mounted 'data' folder
        project_path = "/app/data/yearly_report.qgz"
        project.write(project_path)
        print(f"✅ Success! Project saved to {project_path}")

    # Cleanup
    qgs.exitQgis()
