# VIS Workspace Guide & Antigravity Instructions

## Workspace Overview
Proyek ini adalah web app **VIS (Vertical Infographic Stream) Computer Science & Technology**.

## Arsitektur & Aturan Desain (MANDATORY)
Baca dan patuhi selalu aturan di [`DESIGN_STANDARDS.md`](DESIGN_STANDARDS.md):
1. **Data Source**: Menggunakan `data.js` (`window.libraryData`).
2. **Reader Architecture**: Wajib mempertahankan `#readerView`, `#doomFeed` dengan `aspect-ratio: 1 / 3` (Zero CLS), `#readerNav` (tap-to-toggle, auto-hide scroll), `#navPickerBtn` + `#navPickerDropdown` (article jump picker), `IntersectionObserver` proactive runway lazy loader (`idx-2` s/d `idx+6`), dan pixel-accurate reading memory (`localStorage['vis_tech_positions']`).
3. **Pemisahan Desain**: Desain baru dibuat di folder `designs/` (misal: `designs/variant-X.html`).
4. **Pergantian Desain ke Root**:
   - Backup `index.html` jika diperlukan.
   - Ganti `index.html` dengan template yang dipilih.
   - Ubah `<script src="../data.js">` menjadi `<script src="data.js">`.
   - Jalankan `python update.py --reindex` jika ada folder/poster baru (hanya mengupdate `data.js`).
5. **Dilarang**: Jangan pernah menanamkan string HTML hardcoded ke dalam `update.py`. `update.py` hanya bertugas membaca folder poster dan memperbarui `data.js` serta sinkronisasi git.
