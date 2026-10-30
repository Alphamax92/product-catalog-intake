import os
import shutil
import re
import csv
import json
from datetime import datetime
from excel_generator import generate_catalog_excel

def sanitize_filename(name):
    """Sanitize string for folder and file names."""
    if not name:
        return "unnamed"
    clean = re.sub(r'[\\/*?:"<>|]', '_', str(name).strip())
    clean = re.sub(r'\s+', ' ', clean)
    return clean[:80].strip()

def get_default_drive_path():
    """Detect Google Drive directory or fallback to Documents."""
    candidates = [
        r"G:\My Drive\Product Catalog",
        os.path.expanduser(r"~\Google Drive\Product Catalog"),
        os.path.expanduser(r"~\Documents\Product Catalog")
    ]
    for p in candidates:
        drive_root = os.path.splitdrive(p)[0]
        if drive_root and os.path.exists(drive_root):
            return p
    return os.path.abspath("./Catalog_Output")

def generate_woocommerce_csv(products, csv_path):
    """
    Generates standard WordPress WooCommerce product import CSV.
    """
    fieldnames = [
        "Type", "SKU", "Name", "Published", "Is featured?", "Visibility in catalog",
        "Description", "In stock?", "Regular price", "Regular price (USD)", "Regular price (NGN)",
        "Categories", "Tags", "Images",
        "Attribute 1 name", "Attribute 1 value(s)", "Attribute 1 visible", "Attribute 1 global"
    ]
    
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx, prod in enumerate(products):
            p_name = prod.get("name", f"Product {idx+1}")
            p_type = prod.get("type", "General")
            p_desc = prod.get("description", "")
            p_vendor = prod.get("vendor", "")
            p_stock = 1 if prod.get("in_stock", True) else 0
            
            p_cost_usd = prod.get("unit_cost_usd", prod.get("unit_cost", 0.0))
            p_cost_ngn = prod.get("unit_cost_ngn", 0.0)
            primary_price = p_cost_ngn if p_cost_ngn else p_cost_usd
            
            p_sizes = prod.get("sizes", "")
            p_dims = prod.get("size", "")
            
            attr_values = []
            if p_sizes: attr_values.append(p_sizes)
            if p_dims: attr_values.append(f"Dimensions: {p_dims}")
            attr_val_str = ", ".join(attr_values)
            
            sku = f"WC-{idx+1:04d}"
            
            image_names = []
            if prod.get("image_path"):
                image_names.append(os.path.basename(prod.get("image_path")))
            for g in prod.get("gallery_paths", []):
                image_names.append(os.path.basename(g))
            images_csv = ", ".join(image_names)
            
            writer.writerow({
                "Type": "simple",
                "SKU": sku,
                "Name": p_name,
                "Published": 1,
                "Is featured?": 0,
                "Visibility in catalog": "visible",
                "Description": p_desc,
                "In stock?": p_stock,
                "Regular price": primary_price if primary_price else "",
                "Regular price (USD)": p_cost_usd if p_cost_usd else "",
                "Regular price (NGN)": p_cost_ngn if p_cost_ngn else "",
                "Categories": p_type,
                "Tags": p_vendor,
                "Images": images_csv,
                "Attribute 1 name": "Size" if attr_val_str else "",
                "Attribute 1 value(s)": attr_val_str,
                "Attribute 1 visible": 1 if attr_val_str else "",
                "Attribute 1 global": 1 if attr_val_str else ""
            })

def sort_and_save_catalog(catalog_data, target_drive_dir=None):
    """
    Sorts products into Google Drive folders, saves multiple photos per product,
    creates styled Excel file (with both USD and NGN, NO sum row), and creates WooCommerce import CSV.
    """
    client_name = sanitize_filename(catalog_data.get("client_name", "Client"))
    catalog_title = sanitize_filename(catalog_data.get("catalog_title", "Catalog"))
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    folder_name = f"{client_name}_{catalog_title}_{timestamp}"
    
    if not target_drive_dir:
        target_drive_dir = get_default_drive_path()
        
    catalog_root = os.path.join(target_drive_dir, folder_name)
    os.makedirs(catalog_root, exist_ok=True)
    
    vendor_root = os.path.join(catalog_root, "Products_By_Vendor")
    category_root = os.path.join(catalog_root, "Products_By_Category")
    os.makedirs(vendor_root, exist_ok=True)
    os.makedirs(category_root, exist_ok=True)
    
    excel_products = []
    
    for idx, prod in enumerate(catalog_data.get("products", [])):
        p_name = prod.get("name", f"Product_{idx+1}")
        p_type = prod.get("type", "Uncategorized")
        p_desc = prod.get("description", "")
        p_vendor = prod.get("vendor", "General")
        p_stock = prod.get("in_stock", True)
        p_cost_usd = prod.get("unit_cost_usd", prod.get("unit_cost", 0.0))
        p_cost_ngn = prod.get("unit_cost_ngn", 0.0)
        p_sizes = prod.get("sizes", "")
        p_size_dims = prod.get("size", "")
        
        clean_name = sanitize_filename(p_name)
        clean_type = sanitize_filename(p_type)
        clean_vendor = sanitize_filename(p_vendor)
        
        v_dest_dir = os.path.join(vendor_root, clean_vendor, clean_type, clean_name)
        c_dest_dir = os.path.join(category_root, clean_type, clean_name)
        
        os.makedirs(v_dest_dir, exist_ok=True)
        os.makedirs(c_dest_dir, exist_ok=True)
        
        primary_image_path = None
        gallery_paths = []
        
        images = prod.get("images", [])
        if not isinstance(images, list):
            images = [images] if images else []
            
        for img_idx, img_source in enumerate(images):
            if not img_source or not os.path.exists(img_source):
                continue
                
            ext = os.path.splitext(img_source)[1] or ".png"
            if img_idx == 0:
                dest_filename = f"01_featured_{clean_name}{ext}"
            else:
                dest_filename = f"{img_idx+1:02d}_gallery_{img_idx}_{clean_name}{ext}"
            
            v_img_path = os.path.join(v_dest_dir, dest_filename)
            shutil.copy2(img_source, v_img_path)
            
            c_img_path = os.path.join(c_dest_dir, dest_filename)
            shutil.copy2(img_source, c_img_path)
            
            if img_idx == 0:
                primary_image_path = v_img_path
            else:
                gallery_paths.append(v_img_path)
                
        excel_products.append({
            "name": p_name,
            "type": p_type,
            "description": p_desc,
            "vendor": p_vendor,
            "in_stock": p_stock,
            "unit_cost_usd": p_cost_usd,
            "unit_cost_ngn": p_cost_ngn,
            "unit_cost": p_cost_usd,
            "sizes": p_sizes,
            "size": p_size_dims,
            "image_path": primary_image_path,
            "gallery_paths": gallery_paths
        })
        
    # Generate the exact-match Excel file (NO sum formula)
    excel_path = os.path.join(catalog_root, f"{client_name}_Product_Catalog.xlsx")
    generate_catalog_excel(excel_products, excel_path, client_name=client_name)
    
    # Generate WooCommerce Import CSV
    woo_csv_path = os.path.join(catalog_root, f"{client_name}_woocommerce_import.csv")
    generate_woocommerce_csv(excel_products, woo_csv_path)
    
    # Save manifest JSON
    manifest = {
        "client_name": catalog_data.get("client_name"),
        "catalog_title": catalog_data.get("catalog_title"),
        "created_at": datetime.now().isoformat(),
        "total_records": len(excel_products),
        "categories": list(set(p.get("type") for p in excel_products if p.get("type"))),
        "products": excel_products
    }
    manifest_path = os.path.join(catalog_root, "catalog_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    # Create downloadable zip archive
    zip_base = os.path.join(target_drive_dir, folder_name)
    shutil.make_archive(zip_base, 'zip', catalog_root)
    zip_path = f"{zip_base}.zip"
    
    return {
        "status": "success",
        "catalog_root": catalog_root,
        "excel_path": excel_path,
        "woocommerce_csv_path": woo_csv_path,
        "zip_path": zip_path,
        "total_products": len(excel_products)
    }
