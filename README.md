# PrincessMaker2RefineTranslateTool

**PM2RefineV56TranslateTool** is a translation tool for *Princess Maker 2 Refine*. It is a hex editor with quality-of-life features for translation. It can also be used for other PC games with hex-editable text.  

**PM2DataTool** extracts and injects `.dat` images with automatic padding and color filtering.

---

## PM2RefineV56TranslateTool

This tool is essentially a hex editor, but enhanced with QoL features:
- Easier text selection  
- Compare translated text with the original  
- Automatic backups  
- Automatic padding  
- Includes a pointer relocation feature (may not always work)

### Usage
1. Open the **"Hex Görünümü"** section  
2. Select the text and click **"Orjinale Gönder"**  
3. The text will appear on the right panel  
4. Enter your translation below  
5. Click **Kaydet** to apply changes  
6. Save the `.exe` from the top-left menu  

> Note: **"PE Analiz"** and **"EXE Fark"** are kinda experimental, so they might act weird

## Screenshots

<table>
  <tr>
    <td><img src="https://i.imgur.com/P5xL0R7.png" alt="PM2RefineV56TranslateTool" width="400"></td>
    <td><img src="https://i.imgur.com/mqO3ixt.png" alt="PM2DataTool" width="400"></td>
  </tr>
</table>

---

## PM2DataTool

This tool extracts `.dat` files from *Princess Maker 2 Refine* as PNG images and injects them back.

### Usage
- Put edited files into the **"enjekte_edilecekler"** folder without renaming them. If the folder does not exist next to the `.py` file, create a folder named **"enjekte_edilecekler"** and place the files inside.  
- Use the **"DÜZENLENENLERİ GÖM (İçerideki Dosyayı Kopyala)"** option  
- The tool will automatically match them with the original `.dat`  

Features:
- Warns if the new file is larger than the original  
- Adds padding if the file is smaller  
- Injects images properly with correct alignment  
- May apply color filtering (not sure if available)

This project was generated using AI tools with minimal manual intervention.
