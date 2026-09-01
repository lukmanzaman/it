# VIS (Vertical Infographic Stream) Design & Architecture Standards

Dokumen ini adalah **kontrak arsitektur baku** untuk proyek VIS Computer Science & Technology. Dokumen ini memisahkan secara tegas antara **KOMPONEN PASTI (Fixed Architectural Contract)** dan **KOMPONEN VARIABEL (Free Design Canvas)** untuk memastikan pembuatan template baru atau pergantian desain `index.html` dapat dilakukan secara instan, presisi, dan bebas bug.

---

## 🔒 1. KOMPONEN PASTI (Fixed Architecture - DILARANG DIUBAH)
Setiap desain (baik di `index.html` maupun di folder `designs/`) WAJIB menggunakan struktur, fungsi JavaScript, dan ID/Class berikut secara utuh tanpa modifikasi logika:

### A. Sumber Data (`data.js`)
- Di root (`index.html`): `<script src="data.js"></script>` dan `const libraryData = window.libraryData || [];`
- Di subfolder (`designs/variant-X.html`): `<script src="../data.js"></script>` dan sesuaikan image URL jika diperlukan.
- Dataset memuat struktur:
  ```json
  [
    {
      "rawName": "E1-01-history-computing",
      "number": "01",
      "code": "E1-01",
      "themeCode": "E1",
      "themeTitle": "History of Computing & Tech Culture",
      "themeShortTitle": "Computing & Tech History",
      "displayName": "History of Computing",
      "imageCount": 30,
      "theme": { "bg": "#EFF6FF", "border": "#BFDBFE", "accent": "#2563EB", "icon": "💻" },
      "images": [
        { "name": "the-abacus.png", "cleanTitle": "The Abacus", "url": "E1-01-history-computing/the-abacus.png", "size": "1.2 MB" }
      ]
    }
  ]
  ```

### B. Reader DOM Core (`#readerView`)
Struktur HTML Reader di bawah ini adalah mutlak:
```html
<div id="readerView" style="display: none; width: 100%; min-height: 100vh; background-color: #180914;">
    <!-- Floating Navigation Bar -->
    <nav class="reader-nav nav-hidden" id="readerNav" onclick="event.stopPropagation();">
        <button type="button" class="nav-back-btn" onclick="closeReader();">
            <span>← Kembali</span>
        </button>
        <span class="nav-title-text" id="navFolderTitle">Judul Folder</span>

        <!-- Article Jump Picker Dropdown -->
        <div style="position: relative;">
            <button type="button" class="nav-picker-btn" id="navPickerBtn" onclick="togglePickerDropdown();">
                <span id="navPickerLabel">#1 Judul Artikel</span>
                <span>▾</span>
            </button>
            <div class="nav-picker-dropdown" id="navPickerDropdown">
                <div class="nav-picker-header">
                    <span>PILIH ARTIKEL</span>
                    <span class="picker-total-badge" id="pickerTotalBadge">0 Item</span>
                </div>
                <div class="nav-picker-list" id="navPickerList"></div>
            </div>
        </div>

        <button type="button" class="nav-fullscreen-btn" onclick="toggleFullScreen();">
            <span>⛶</span>
        </button>
    </nav>

    <!-- Continuous Infographic Stream -->
    <main class="doom-feed" id="doomFeed"></main>

    <!-- Scroll Memory Toast -->
    <div class="restore-toast" id="restoreToast">
        <span id="restoreToastText">Melanjutkan membaca...</span>
    </div>
</div>
```

### C. Kontrak CSS Reader (Zero Cumulative Layout Shift / CLS)
- `.article-frame`: WAJIB `aspect-ratio: 1 / 3` dan `width: 100%`.
- `.article-img`: `width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity 0.2s;`
- `.article-img.is-loaded`: `opacity: 1;`
- `.reader-nav`: `position: fixed; top: 14px; left: 50%; transform: translateX(-50%); z-index: 9999;`
- `.reader-nav.nav-hidden`: `opacity: 0 !important; visibility: hidden !important; pointer-events: none !important;`

### D. Engine JavaScript Inti (Standar Wajib)
1. **Interactive Navigation & Jump Picker**:
   - `showNav()`, `hideNav()`, `toggleNav()`.
   - `togglePickerDropdown()`, `closePickerDropdown()`.
   - `updateActiveArticleState(artNum)`: memperbarui teks `#navPickerLabel` dan status `.active` pada `#navPickerList`.
   - Tap-to-toggle nav: Tap layar bagian atas (`e.clientY <= 90`) memunculkan nav, klik di luar atau scrolling otomatis menyembunyikan nav.
2. **Proactive Runway Lazy Loading Engine**:
   - Menggunakan `IntersectionObserver` dengan `rootMargin: '600px 0px'`.
   - `preloadRunway(currentIdx)`: Me-load frame `idx - 2` hingga `idx + 6`.
   - `preloadImageUrl(url)` menggunakan cache `preloadedUrls = new Set()` dan `new Image()` preheating dengan `decoding = 'async'`.
   - Cleanup: `imageObserver.disconnect()` dipanggil saat `closeReader()`.
3. **Pixel-Accurate Position Memory**:
   - Kunci LocalStorage: `'vis_tech_positions'` -> `{ [folderRawName]: { artIdx, scrollY, total, ts } }`.
   - Simpan posisi pada event `scroll` (debounced 100ms), `beforeunload`, dan `pagehide`.
   - Pemulihan posisi: `window.scrollTo({ top: savedPos.scrollY, behavior: 'instant' })` dengan flag `isRestoringScroll` agar tidak saling menimpa.
   - Menampilkan notifikasi `#restoreToast` ("Melanjutkan dari artikel #X").

---

## 🎨 2. KOMPONEN VARIABEL (Free Design Canvas)
*Hanya komponen di bawah ini yang dirancang ulang / dimodifikasi pada varian desain baru:*

1. **Struktur & Tata Letak Home Screen (`#homeView`)**:
   - Konsep UI: Dual-Pane Studio, 3D Matrix / Museum Grid, Skill-Tree Roadmap, Bento Box, Masonry Wall, Horizontal Stream, Magazine Spread, dll.
   - Komponen interaktif: Input pencarian live, filter chip domain (`E1` - `E6`), tab switcher, moodboard preview.
2. **Tema Visual & Styling**:
   - Skema warna (`--bg`, `--card`, `--text-heading`, `--text-body`, `--pink-glow`, `--accent`, dll).
   - Tipografi Google Fonts (Space Grotesk, Plus Jakarta Sans, Syne, Outfit, JetBrains Mono, dll).
   - Efek visual: Glassmorphism, Neumorphism, Cyber Glow, Soft Shadows, Borders.

---

## ⚡ 3. Protokol Pergantian Desain Cepat (1 Detik)
Untuk mengganti desain utama `index.html` dari salah satu file di `designs/`:
1. Buat backup `index.backup.html` jika diperlukan.
2. Salin isi file template dari `designs/variant-X.html`.
3. Sesuaikan path:
   - `<script src="../data.js">` -> `<script src="data.js">`
   - Hapus pemrosesan prefix `../` pada `libraryData` (di root path URL gambar sudah relatif terhadap CWD).
4. Tulis langsung ke `index.html`.
5. Skrip [`update.py`](file:///E:/FAKTA-CERITA-EKSPANSI/FAKTA-AGY/POSTER/E/update.py) hanya bertugas memindai folder/gambar dan menulis `data.js` tanpa menimpa template `index.html`.
