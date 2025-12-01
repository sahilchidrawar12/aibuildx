# Quick Start: DWG→Tekla Conversion

## 5-Minute Setup

### 1. Install Dependencies

```bash
source .venv/bin/activate
pip install flask ezdxf ifcopenshell numpy -q
echo "✅ Ready!"
```

### 2. Start Web Server

```bash
python app.py
# Navigate to http://localhost:5000
```

### 3. Upload & Convert

- Drag-and-drop your DWG file
- Click "Upload & Process"
- Wait for completion
- Download results or export to Tekla

---

## CLI Usage (Batch / Automation)

### Single File

```bash
python cli.py convert --input drawing.dwg --output ./model_output --verbose
```

### Batch Processing

```bash
python cli.py batch --config example_batch_config.json --verbose
```

### Validation

```bash
python cli.py validate --input output/final.json
```

---

## Tekla Import

### Via IFC (Recommended)

1. Web UI → Download `model.ifc`
2. Tekla Structures → File → Import → IFC
3. Select file and import

### Via .NET API

```csharp
using TeklaStructures.AIBuildX;

var builder = new TeklaModelBuilder();
var result = builder.ImportMembers("output/final.json", "MyModel");
Console.WriteLine(result.Message);
```

---

## Output Files

After conversion:

| File | Purpose |
|------|---------|
| `final.json` | Corrected 3D model (all members, connections) |
| `model.ifc` | LOD500 IFC for Tekla import |
| `cnc.csv` | Fabrication bill |
| `reporter.json` | BOM + summary |
| `clashes.json` | Clash detection results |

---

## Troubleshooting

**Q: Port 5000 already in use?**
```bash
python cli.py web --port 8080
```

**Q: DWG file not recognized?**
- Ensure layers are named: `BEAMS`, `COLUMNS`, `BRACES`
- Export from AutoCAD as DWG format

**Q: Tekla import fails?**
- Check Tekla Open API is enabled (Tools → Options → Advanced)
- Verify model.ifc was generated
- Check Tekla version is 2021+

---

## Test Everything

```bash
pytest tests/test_tekla_integration.py -v
```

Expected: **12 passed** ✅

---

For full documentation, see **TEKLA_INTEGRATION_GUIDE.md**
