import os
import socket
import psycopg2
import requests
from qgis.core import QgsApplication
from tabulate import tabulate


def test_internet():
    print("--- 1. Testing Internet Access (Proxy Check) ---")
    url = "https://www.google.com"
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Success! Reached {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Failed! Cannot reach internet. Check HTTP_PROXY settings.")
        print(f"Error: {e}")


def test_db_network():
    print("\n--- 2. Testing Database Network Reachability ---")
    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT', 5432))
    try:
        # socket checks if the 'road' to the IP/Port is open
        with socket.create_connection((host, port), timeout=5):
            print(f"✅ Success! Port {port} on {host} is reachable.")
    except Exception as e:
        print(f"❌ Failed! Cannot reach {host}:{port}. Is it in NO_PROXY?")
        print(f"Error: {e}")


def test_db_credentials():
    print("\n--- 3. Testing Database Login (psycopg2) ---")
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            port=os.getenv('DB_PORT')
        )
        print("✅ Success! Database login successful.")
        conn.close()
    except Exception as e:
        print(f"❌ Failed! Network is fine, but credentials or DB permissions failed.")
        print(f"Error: {e}")


def test_qgis_init():
    print("\n--- 4. Testing QGIS Headless Initialization ---")
    try:
        # Initialize QGIS
        qgs = QgsApplication([], False)
        qgs.initQgis()
        print(f"✅ Success! QGIS {qgs.applicationVersion()} initialized in headless mode.")
        qgs.exitQgis()
    except Exception as e:
        print(f"❌ Failed! QGIS libraries are not correctly linked in Docker.")
        print(f"Error: {e}")


def test_data_fetch():
    print("\n--- 5. Testing End-to-End Data Fetch (Permissions Check) ---")
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            port=os.getenv('DB_PORT'),
            connect_timeout=5
        )
        cur = conn.cursor()

        # We use a very light query with a LIMIT to avoid heavy DB load
        # Testing access to the specific view mentioned in your SQL
        query = """
            SELECT gewaesser, name, jahr, summe 
            FROM fiaka_use.view_arten_biotop_utm 
            LIMIT 5;
        """
        
        print(f"Executing: Fetching 5 rows from fiaka_use.view_arten_biotop_utm...")
        cur.execute(query)
        rows = cur.fetchall()

        if rows:
            print(f"✅ Success! Retrieved {len(rows)} rows.")
            # Formatting the output for clarity
            headers = ["Gewaesser", "Artname", "Jahr", "Summe"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        else:
            print("⚠️ Connected, but the view returned 0 rows. (Check if VIEW is populated)")

        cur.close()
    except psycopg2.Error as e:
        print(f"❌ Failed! Database permission or schema error.")
        print(f"Error Code: {e.pgcode}")
        print(f"Error Message: {e.pgerror}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print(f"Environment Check: HTTP_PROXY is {os.getenv('HTTP_PROXY')}")
    test_internet()
    test_db_network()
    test_db_credentials()
    test_qgis_init()
    test_data_fetch()
    # TODO: Write a new test that gets some data from fiaka DB and prints it out, to confirm full end-to-end connectivity and permissions.