import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.utils import get_column_letter
from PIL import Image as PILImage
import os

BASE_PALETTE = [
    {"fill": "FCE7F3", "font": "9D174D", "stripe": "EC4899"}, # Pink
    {"fill": "FEF3C7", "font": "92400E", "stripe": "F59E0B"}, # Amber
    {"fill": "E0F2FE", "font": "0369A1", "stripe": "0EA5E9"}, # Sky
    {"fill": "EDE9FE", "font": "6D28D9", "stripe": "8B5CF6"}, # Purple
    {"fill": "FEF9C3", "font": "854D0E", "stripe": "EAB308"}, # Yellow
    {"fill": "DCFCE7", "font": "15803D", "stripe": "22C55E"}, # Green
    {"fill": "FEE2E2", "font": "B91C1C", "stripe": "EF4444"}, # Rose
    {"fill": "E0E7FF", "font": "3730A3", "stripe": "6366F1"}, # Indigo
    {"fill": "CCFBF1", "font": "115E59", "stripe": "14B8A6"}, # Teal
]

def get_type_style(cat_name):
    if not cat_name:
        return {"fill": "F3F4F6", "font": "374151", "stripe": "9CA3AF"}
    idx = abs(hash(cat_name)) % len(BASE_PALETTE)
    return BASE_PALETTE[idx]

def generate_catalog_excel(products, output_path, client_name="Client Catalog"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Products"
    ws.views.sheetView[0].showGridLines = True
    
    VENDOR_FILL = "EEF2F6"
    VENDOR_FONT = "334155"
    HEADER_FILL = "F8FAFC"
    HEADER_FONT = "475569"
    BORDER_COLOR = "E2E8F0"
    
    thin_border = Border(
        left=Side(style='thin', color=BORDER_COLOR),
        right=Side(style='thin', color=BORDER_COLOR),
        top=Side(style='thin', color=BORDER_COLOR),
        bottom=Side(style='thin', color=BORDER_COLOR)
    )
    
    # Headers with both Dollar ($) and Naira (₦), Sizes, Size (WxLxH), Description
    # NO total sum formula
    headers = [
        "", "Name", "Type", "Images", "Description", "In stock",
        "Unit cost ($)", "Unit cost (₦)", "Sizes", "Size (WxLxH)"
    ]
    ws.append(headers)
    ws.row_dimensions[1].height = 32
    
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = Font(name="Segoe UI", size=10, bold=True, color=HEADER_FONT)
        cell.fill = PatternFill(start_color=HEADER_FILL, end_color=HEADER_FILL, fill_type="solid")
        cell.alignment = Alignment(
            horizontal="center" if col_idx in [1, 3, 4, 6] else ("right" if col_idx in [7, 8] else "left"),
            vertical="center"
        )
        cell.border = thin_border
        
    ws.column_dimensions["A"].width = 3.5    # Stripe
    ws.column_dimensions["B"].width = 28     # Name
    ws.column_dimensions["C"].width = 18     # Type
    ws.column_dimensions["D"].width = 22     # Images
    ws.column_dimensions["E"].width = 30     # Description
    ws.column_dimensions["F"].width = 12     # In stock
    ws.column_dimensions["G"].width = 16     # Unit cost ($)
    ws.column_dimensions["H"].width = 18     # Unit cost (₦)
    ws.column_dimensions["I"].width = 16     # Sizes
    ws.column_dimensions["J"].width = 24     # Size (WxLxH)
    
    start_row = 2
    temp_resized_images = []
    
    for idx, prod in enumerate(products):
        row = start_row + idx
        ws.row_dimensions[row].height = 78
        
        prod_type = prod.get("type", "").strip()
        type_style = get_type_style(prod_type)
        
        # Col A: Stripe
        cell_a = ws.cell(row=row, column=1)
        cell_a.fill = PatternFill(start_color=type_style["stripe"], end_color=type_style["stripe"], fill_type="solid")
        cell_a.border = Border(top=Side(style='thin', color=BORDER_COLOR), bottom=Side(style='thin', color=BORDER_COLOR))
        
        # Col B: Name
        cell_b = ws.cell(row=row, column=2, value=prod.get("name", ""))
        cell_b.font = Font(name="Segoe UI", size=10, bold=True, color="1E293B")
        cell_b.alignment = Alignment(horizontal="left", vertical="center")
        cell_b.border = thin_border
        
        # Col C: Type
        cell_c = ws.cell(row=row, column=3, value=prod_type)
        cell_c.font = Font(name="Segoe UI", size=9, bold=True, color=type_style["font"])
        cell_c.fill = PatternFill(start_color=type_style["fill"], end_color=type_style["fill"], fill_type="solid")
        cell_c.alignment = Alignment(horizontal="center", vertical="center")
        cell_c.border = thin_border
        
        # Col D: Images
        cell_d = ws.cell(row=row, column=4, value="")
        cell_d.border = thin_border
        cell_d.alignment = Alignment(horizontal="center", vertical="center")
        
        primary_image = prod.get("image_path")
        gallery_images = prod.get("gallery_paths", [])
        total_photos_count = (1 if primary_image else 0) + len(gallery_images)
        
        if primary_image and os.path.exists(primary_image):
            try:
                with PILImage.open(primary_image) as pil_img:
                    pil_img = pil_img.convert("RGB")
                    pil_img.thumbnail((120, 85))
                    temp_thumb = f"{primary_image}_thumb_{row}.png"
                    pil_img.save(temp_thumb)
                    temp_resized_images.append(temp_thumb)
                    
                    xl_img = OpenpyxlImage(temp_thumb)
                    ws.add_image(xl_img, f"D{row}")
                    
                    if len(gallery_images) > 0:
                        cell_d.value = f"+{len(gallery_images)} more"
                        cell_d.font = Font(name="Segoe UI", size=8, color="64748B")
                        cell_d.alignment = Alignment(horizontal="right", vertical="bottom")
            except Exception as e:
                cell_d.value = f"[{total_photos_count} Images]"
        elif total_photos_count > 0:
            cell_d.value = f"[{total_photos_count} Images]"
        
        # Col E: Description
        cell_e = ws.cell(row=row, column=5, value=prod.get("description", ""))
        cell_e.font = Font(name="Segoe UI", size=9, color="334155")
        cell_e.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell_e.border = thin_border
        
        # Col F: In stock
        in_stock = prod.get("in_stock", False)
        cell_f = ws.cell(row=row, column=6, value="👍" if in_stock else "")
        cell_f.font = Font(name="Segoe UI Emoji", size=12)
        cell_f.alignment = Alignment(horizontal="center", vertical="center")
        cell_f.border = thin_border
        
        # Col G: Unit cost ($ USD)
        cost_usd = prod.get("unit_cost_usd", prod.get("unit_cost", 0.0))
        try:
            if isinstance(cost_usd, str):
                cost_usd = float(cost_usd.replace("$", "").replace(",", "").strip())
        except:
            cost_usd = 0.0
        cell_g = ws.cell(row=row, column=7, value=cost_usd if cost_usd else "")
        cell_g.number_format = '"$"#,##0.00'
        cell_g.font = Font(name="Segoe UI", size=10, color="1E293B")
        cell_g.alignment = Alignment(horizontal="right", vertical="center")
        cell_g.border = thin_border
        
        # Col H: Unit cost (₦ NGN)
        cost_ngn = prod.get("unit_cost_ngn", 0.0)
        try:
            if isinstance(cost_ngn, str):
                cost_ngn = float(cost_ngn.replace("₦", "").replace(",", "").strip())
        except:
            cost_ngn = 0.0
        cell_h = ws.cell(row=row, column=8, value=cost_ngn if cost_ngn else "")
        cell_h.number_format = '"₦"#,##0.00'
        cell_h.font = Font(name="Segoe UI", size=10, color="1E293B")
        cell_h.alignment = Alignment(horizontal="right", vertical="center")
        cell_h.border = thin_border
        
        # Col I: Sizes (e.g. S, M, L or Standard)
        cell_i = ws.cell(row=row, column=9, value=prod.get("sizes", ""))
        cell_i.font = Font(name="Segoe UI", size=9, color="334155")
        cell_i.alignment = Alignment(horizontal="center", vertical="center")
        cell_i.border = thin_border
        
        # Col J: Size (WxLxH) (Dimensions)
        cell_j = ws.cell(row=row, column=10, value=prod.get("size", ""))
        cell_j.font = Font(name="Segoe UI", size=9, color="334155")
        cell_j.alignment = Alignment(horizontal="left", vertical="center")
        cell_j.border = thin_border

    # Footer Row: Record count ONLY. NO TOTAL SUM FORMULA as requested.
    summary_row = start_row + len(products)
    ws.row_dimensions[summary_row].height = 24
    cell_rec = ws.cell(row=summary_row, column=2, value=f"{len(products)} records")
    cell_rec.font = Font(name="Segoe UI", size=9, bold=True, color="64748B")
    cell_rec.alignment = Alignment(horizontal="left", vertical="center")
        
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb.save(output_path)
    
    for t in temp_resized_images:
        try:
            if os.path.exists(t):
                os.remove(t)
        except:
            pass
            
    return output_path
