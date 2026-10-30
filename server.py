import os
import json
import base64
import tempfile
from flask import Flask, request, jsonify, send_file
import drive_sorter
from drive_sorter import sort_and_save_catalog, get_default_drive_path

app = Flask(__name__, static_folder="static")

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.route("/")
def index():
    html_file = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    return "<h1>Product Catalog Portal</h1><p>index.html not found.</p>"

@app.route("/client")
def client_view():
    html_file = os.path.join(os.path.dirname(__file__), "client_portal.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    return "<h1>Client Portal</h1><p>client_portal.html not found.</p>"

@app.route("/api/drive-status", methods=["GET"])
def drive_status():
    default_path = get_default_drive_path()
    g_drive_detected = os.path.exists(r"G:\My Drive")
    return jsonify({
        "detected_path": default_path,
        "is_google_drive_connected": g_drive_detected,
        "drive_letter": "G:\\" if g_drive_detected else None
    })

@app.route("/api/sample", methods=["GET"])
def get_sample_data():
    sample_json = os.path.join(os.path.dirname(__file__), "sample_data.json")
    if os.path.exists(sample_json):
        with open(sample_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify([])

@app.route("/api/save-catalog", methods=["POST"])
def save_catalog():
    try:
        data = request.get_json(force=True)
        client_name = data.get("client_name", "Client")
        catalog_title = data.get("catalog_title", "Catalog")
        custom_drive_path = data.get("target_folder")
        raw_products = data.get("products", [])

        temp_img_files = []
        processed_products = []

        for p in raw_products:
            local_img_paths = []
            
            raw_images = p.get("images", [])
            if not raw_images and p.get("image_data"):
                raw_images = [p.get("image_data")]
            elif isinstance(raw_images, str):
                raw_images = [raw_images]
                
            for img_b64 in raw_images:
                if not img_b64: continue
                if "base64," in img_b64:
                    try:
                        header, encoded = img_b64.split("base64,", 1)
                        ext = ".png"
                        if "image/jpeg" in header or "image/jpg" in header:
                            ext = ".jpg"
                        elif "image/webp" in header:
                            ext = ".webp"
                        
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                        tmp.write(base64.b64decode(encoded))
                        tmp.close()
                        local_img_paths.append(tmp.name)
                        temp_img_files.append(tmp.name)
                    except Exception as ex:
                        print("Error decoding image:", ex)
                elif os.path.exists(img_b64):
                    local_img_paths.append(img_b64)

            # Both USD and NGN prices
            cost_usd = p.get("unit_cost_usd", p.get("unit_cost", 0.0))
            cost_ngn = p.get("unit_cost_ngn", 0.0)

            processed_products.append({
                "name": p.get("name", "Untitled Product"),
                "type": p.get("type", "General"),
                "description": p.get("description", ""),
                "vendor": p.get("vendor", ""),
                "in_stock": bool(p.get("in_stock", True)),
                "unit_cost_usd": cost_usd,
                "unit_cost_ngn": cost_ngn,
                "unit_cost": cost_usd,
                "sizes": p.get("sizes", ""),
                "size": p.get("size", ""),
                "images": local_img_paths
            })

        payload = {
            "client_name": client_name,
            "catalog_title": catalog_title,
            "products": processed_products
        }

        result = sort_and_save_catalog(payload, target_drive_dir=custom_drive_path)

        for tmp_file in temp_img_files:
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except:
                pass

        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/open-folder", methods=["POST"])
def open_folder():
    try:
        data = request.get_json(force=True)
        folder_path = data.get("folder_path")
        if folder_path and os.path.exists(folder_path):
            os.startfile(folder_path)
            return jsonify({"status": "opened", "path": folder_path})
        return jsonify({"status": "error", "message": "Folder does not exist"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/download-excel", methods=["GET"])
def download_excel():
    excel_path = request.args.get("path")
    if excel_path and os.path.exists(excel_path):
        return send_file(excel_path, as_attachment=True, download_name=os.path.basename(excel_path))
    return "File not found", 404

@app.route("/api/download-woo-csv", methods=["GET"])
def download_woo_csv():
    csv_path = request.args.get("path")
    if csv_path and os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True, download_name=os.path.basename(csv_path))
    return "File not found", 404

@app.route("/api/download-zip", methods=["GET"])
def download_zip():
    zip_path = request.args.get("path")
    if zip_path and os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=os.path.basename(zip_path))
    return "File not found", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"Starting Product Catalog Intake Server on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
