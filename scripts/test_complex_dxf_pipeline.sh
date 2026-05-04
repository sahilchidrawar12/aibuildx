#!/bin/bash
# Test all 4 challenging DXF files through the pipeline

echo ""
echo "=========================================================="
echo "TESTING 4 CHALLENGING DXF FILES THROUGH PIPELINE"
echo "=========================================================="
echo ""

cd /Users/sahil/Documents/aibuildx

# Test files
files=(
  "test_dxf_1_curved_truss.dxf"
  "test_dxf_2_spiral_staircase.dxf"
  "test_dxf_3_double_curved_dome.dxf"
  "test_dxf_4_complex_junction.dxf"
)

descriptions=(
  "Curved Truss with Arcs and Splines"
  "Spiral Staircase with Helical Members"
  "Double-Curved Dome with Elliptical Sections"
  "Complex Junction with Intersecting Members"
)

results_file="test_results_complex_dxf.json"
echo "{\"test_date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"results\": []}" > "$results_file"

# Test each file
for i in "${!files[@]}"; do
  file="${files[$i]}"
  desc="${descriptions[$i]}"
  test_num=$((i+1))
  
  echo ""
  echo "────────────────────────────────────────────────────────"
  echo "TEST $test_num: $desc"
  echo "────────────────────────────────────────────────────────"
  echo "File: $file"
  echo ""
  
  if [ ! -f "$file" ]; then
    echo "❌ File not found: $file"
    continue
  fi
  
  file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
  echo "File size: $file_size bytes"
  
  # Run pipeline
  start_time=$(date +%s)
  output_dir="outputs/test_${test_num}"
  
  python3 << PYEOF
import sys
sys.path.insert(0, '/Users/sahil/Documents/aibuildx')
from src.pipeline.pipeline_compat import run_pipeline
import json
import time

try:
    print(f"Running pipeline for: $file")
    result = run_pipeline('$file', out_dir='$output_dir')
    
    if result.get('status') == 'error':
        print(f"❌ Pipeline error: {result.get('error', 'Unknown')}")
        exit(1)
    
    # Summarize results
    print("\n✅ Pipeline completed successfully!")
    print("\nResults summary:")
    
    if 'miner' in result:
        members = result['miner'].get('members', [])
        print(f"  • Members detected: {len(members)}")
    
    if 'ifc' in result:
        ifc_data = result['ifc']
        if isinstance(ifc_data, dict):
            beams = ifc_data.get('beams', [])
            columns = ifc_data.get('columns', [])
            plates = ifc_data.get('plates', [])
            fasteners = ifc_data.get('fasteners', [])
            joints = ifc_data.get('joints', [])
            print(f"  • Beams: {len(beams)}")
            print(f"  • Columns: {len(columns)}")
            print(f"  • Plates: {len(plates)}")
            print(f"  • Fasteners: {len(fasteners)}")
            print(f"  • Joints: {len(joints)}")
    
    if 'connections' in result:
        connections = result['connections'].get('connections', [])
        print(f"  • Connections detected: {len(connections)}")
    
    if 'clashes' in result:
        clashes = result['clashes'].get('clashes', [])
        print(f"  • Clashes detected: {len(clashes)}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

PYEOF
  
  exit_code=$?
  end_time=$(date +%s)
  elapsed=$((end_time - start_time))
  
  if [ $exit_code -eq 0 ]; then
    echo ""
    echo "⏱️  Processing time: ${elapsed}s"
    echo "✅ Test $test_num PASSED"
  else
    echo "❌ Test $test_num FAILED (exit code: $exit_code)"
  fi
done

echo ""
echo "=========================================================="
echo "COMPLEX DXF TESTING COMPLETE"
echo "=========================================================="
echo ""
