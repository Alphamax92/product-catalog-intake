# WordPress eCommerce Product Catalog Intake & Google Drive Sorter

A single-session product catalog intake application designed for **WordPress & WooCommerce stores**. It replaces single-response Google Forms with an all-in-one portal where clients define their store categories, enter all products in a single session, attach multiple photos per product, and export both a visual Excel catalog with photo thumbnails and an instant-import WooCommerce CSV.

---

## 🚀 Key Adjustments & Features

### 1. WordPress eCommerce & WooCommerce Integration
* Automatically generates a standardized **`woocommerce_import.csv`** formatted specifically for WordPress WooCommerce (`WooCommerce > Products > Import`).
* Mapped fields:
  * `Name`, `Categories`, `Regular price`, `Regular price (USD)`, `Regular price (NGN)`, `In stock?`, `Tags` (Vendor/Brand)
  * `Attribute 1 name`: **Size**, `Attribute 1 value(s)`: **Sizes & Dimensions**
  * `Images`: Main featured image + all additional gallery photos

### 2. Client Category Setup (Step 1)
* The portal is **universal for any client** (furniture, fashion, beauty, electronics, food, etc.).
* Clients are prompted first with **"Step 1: Set Categories"** to define their store categories (e.g. *Dresses, Tops, Shoes* or *Bookshelves, Chairs, Tables*).
* Includes 1-click industry presets or custom category creation with automatic pastel pill styling.
* Category dropdowns dynamically update to show only their store's categories.

### 3. Dual Currency Tabs in Price (₦ Naira and $ Dollars)
* **Currency Switcher Tabs**: `[ Both (₦ & $) ]`, `[ ₦ NGN ]`, and `[ $ USD ]`.
* Easily toggle views:
  * **Both**: Displays two dedicated columns `Unit cost ($)` and `Unit cost (₦)` side-by-side.
  * **₦ NGN**: Displays Nigerian Naira pricing.
  * **$ USD**: Displays US Dollar pricing.
* Both currency values are stored and exported to the formatted Excel sheet and WooCommerce CSV.

### 4. Multiple Pictures per Product (No Bulk Upload)
* Bulk photo upload has been replaced with clean, per-product photo management.
* Click **"+ Photos"** or any thumbnail on a product to attach multiple pictures.
* Set which image is the **★ Main Featured** image, reorder, or delete extra shots.
* Google Drive auto-sorts all photos into:
  * `Products_By_Category / [Category] / [Product_Name] / 01_featured.jpg, 02_gallery_1.jpg...`
  * `Products_By_Vendor / [Vendor] / [Category] / [Product_Name] / ...`

### 5. Dedicated Sizes Column + Physical Dimensions
* Added a dedicated **`Sizes`** column for clothing/shoe sizes or variants (e.g., `S, M, L`, `Standard`, `Twin / Full / Queen`, `Custom`).
* Retained the **`Size (WxLxH)`** column for physical dimensions (e.g., `12x7x8`, `H 31.75" W 18"`).

### 6. Clean Form Design (No Description Tab & No Total Sum)
* **No Description Tab**: Kept the form lightweight and focused on essential eCommerce intake fields.
* **No Total Sum**: Removed the total catalog sum from both the sticky footer and the Excel export. The footer displays active counts: `+ Add...` • `X records` • `Y in stock` • `Z photos`.

### 7. Dedicated Client-Facing Experience
* **Client Portal ([`client_portal.html`](file:///C:/Users/maxvi/.gemini/antigravity/scratch/product-catalog-collector/client_portal.html))**: A zero-setup, zero-login standalone file you can send directly to your client or access at `http://localhost:8765/client`. Her only job is to fill it out and click **"Download Completed Catalog (.zip)"**.
* **Admin / Drive Sync Mode ([`index.html`](file:///C:/Users/maxvi/.gemini/antigravity/scratch/product-catalog-collector/index.html))**: Accessible at `http://localhost:8765`, connected directly to your Google Drive Desktop sync (`G:\My Drive\Product Catalog`).

---

## 📁 Output Artifacts in Google Drive

When submitted, the system automatically creates:
```
G:\My Drive\Product Catalog\[Client_Name]_[Store]_[Timestamp]/
├── Products_By_Category/
│   ├── Bookshelves/
│   │   └── Samari bookshelf (box + cask)/
│   │       ├── 01_featured_Samari_bookshelf.jpg
│   │       └── 02_gallery_1_Samari_bookshelf.jpg
│   └── Chairs/
├── Products_By_Vendor/
├── [Client_Name]_Product_Catalog.xlsx      <- Formatted Excel with photo thumbnails & dual currency (no sum row)
├── [Client_Name]_woocommerce_import.csv   <- Ready for WordPress WooCommerce Import
├── catalog_manifest.json
└── [Client_Name]_[Timestamp].zip
```

---

## 💻 How to Use

1. **Launch Server**:
   Double click [`run_app.bat`](file:///C:/Users/maxvi/.gemini/antigravity/scratch/product-catalog-collector/run_app.bat) or run:
   ```powershell
   python C:\Users\maxvi\.gemini\antigravity\scratch\product-catalog-collector\server.py
   ```
2. **Open in Browser**:
   * Admin / Sync Portal: [http://localhost:8765](http://localhost:8765)
   * Client-Only Portal: [http://localhost:8765/client](http://localhost:8765/client) or open [`client_portal.html`](file:///C:/Users/maxvi/.gemini/antigravity/scratch/product-catalog-collector/client_portal.html) directly in any browser.
