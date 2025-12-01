#!/usr/bin/env python3
"""
Enhanced pipeline runner that properly handles complex JSON input and
performs deep analysis of Tekla 3D integration requirements.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, "/Users/sahil/Documents/aibuildx")

from src.pipeline.pipeline_compat import run_pipeline

def convert_to_dxf_entities(input_data: Dict) -> List[Dict]:
    """
    Convert our JSON structure into DXF-like entities that the miner can process.
    """
    entities = []
    
    # Convert columns to LINE entities
    for col in input_data.get("columns", []):
        entities.append({
            "type": "LINE",
            "layer": "COLUMNS",
            "start_point": [col["start_x"], col["start_y"], col["start_z"]],
            "end_point": [col["end_x"], col["end_y"], col["end_z"]],
            "id": col["id"],
            "properties": {
                "profile": col.get("profile"),
                "material": col.get("material"),
                "length": col.get("length"),
                "member_type": "COLUMN"
            }
        })
    
    # Convert beams to LINE entities
    for beam in input_data.get("beams", []):
        entities.append({
            "type": "LINE",
            "layer": "BEAMS",
            "start_point": [beam["start_x"], beam["start_y"], beam["start_z"]],
            "end_point": [beam["end_x"], beam["end_y"], beam["end_z"]],
            "id": beam["id"],
            "properties": {
                "profile": beam.get("profile"),
                "material": beam.get("material"),
                "length": beam.get("length"),
                "direction": beam.get("direction"),
                "member_type": "BEAM"
            }
        })
    
    # Convert braces to LINE entities
    for brace in input_data.get("braces", []):
        entities.append({
            "type": "LINE",
            "layer": "BRACES",
            "start_point": [brace["start_x"], brace["start_y"], brace["start_z"]],
            "end_point": [brace["end_x"], brace["end_y"], brace["end_z"]],
            "id": brace["id"],
            "properties": {
                "profile": brace.get("profile"),
                "material": brace.get("material"),
                "length": brace.get("length"),
                "member_type": "BRACE"
            }
        })
    
    # Convert connections to POINT entities with connection data
    for conn in input_data.get("connections", []):
        entities.append({
            "type": "POINT",
            "layer": "CONNECTIONS",
            "point": [conn.get("connection_x"), conn.get("connection_y"), conn.get("connection_z")],
            "id": conn["id"],
            "properties": conn
        })
    
    return entities


def prepare_complex_input(input_json_path: str) -> Dict:
    """Load and prepare input data for pipeline."""
    
    with open(input_json_path) as f:
        input_data = json.load(f)
    
    # Convert to DXF-like entities
    entities = convert_to_dxf_entities(input_data)
    
    # Prepare payload that pipeline expects
    payload = {
        "building_info": input_data.get("building", {}),
        "entities": entities,
        "members_raw": {
            "columns": input_data.get("columns", []),
            "beams": input_data.get("beams", []),
            "braces": input_data.get("braces", [])
        },
        "connections_raw": input_data.get("connections", []),
        "plates_raw": input_data.get("plates", [])
    }
    
    return payload


def run_enriched_pipeline_analysis():
    """Run complex structure through pipeline with deep analysis."""
    
    input_json_path = "/Users/sahil/Documents/aibuildx/examples/complex_structure_input.json"
    output_dir = "/Users/sahil/Documents/aibuildx/examples/pipeline_analysis_enriched"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 90)
    print("🔬 ENRICHED PIPELINE ANALYSIS: Complex 3-Story Steel Building")
    print("=" * 90)
    
    # Load input
    print("\n📥 Loading and preparing input structure...")
    input_data = prepare_complex_input(input_json_path)
    building = input_data["building_info"]
    
    print(f"   ✓ Building: {building.get('name', 'N/A')}")
    print(f"   ✓ Dimensions: {building.get('width')}m x {building.get('length')}m x {building.get('height')}m")
    print(f"   ✓ Columns: {len(input_data['members_raw']['columns'])}")
    print(f"   ✓ Beams: {len(input_data['members_raw']['beams'])}")
    print(f"   ✓ Braces: {len(input_data['members_raw']['braces'])}")
    print(f"   ✓ Connections: {len(input_data['connections_raw'])}")
    
    # Save prepared data
    prepared_json_path = os.path.join(output_dir, "prepared_input.json")
    with open(prepared_json_path, "w") as f:
        json.dump(input_data, f, indent=2)
    print(f"   ✓ Prepared input saved to {prepared_json_path}")
    
    # Run pipeline
    print("\n🔄 Running full 17-agent pipeline...")
    try:
        result = run_pipeline(prepared_json_path, out_dir=output_dir)
        print("   ✓ Pipeline execution complete!")
    except Exception as e:
        print(f"   ⚠️  Pipeline warning: {e}")
        result = {}
    
    # Save enriched result
    result_path = os.path.join(output_dir, "enriched_pipeline_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"   ✓ Result saved to {result_path}")
    
    return result, input_data, output_dir


def deep_tekla_readiness_analysis(result: Dict, input_data: Dict, output_dir: str):
    """Comprehensive analysis for Tekla 3D rendering readiness."""
    
    print("\n" + "=" * 90)
    print("🎯 TEKLA 3D RENDERING READINESS ASSESSMENT")
    print("=" * 90)
    
    analysis = {
        "timestamp": "2025-12-01",
        "structure_info": input_data.get("building_info", {}),
        "assessment": {
            "3d_coordinates": {"status": "PENDING", "score": 0, "details": []},
            "member_properties": {"status": "PENDING", "score": 0, "details": []},
            "connection_definitions": {"status": "PENDING", "score": 0, "details": []},
            "plate_geometry": {"status": "PENDING", "score": 0, "details": []},
            "material_specifications": {"status": "PENDING", "score": 0, "details": []},
            "weld_specifications": {"status": "PENDING", "score": 0, "details": []},
            "bolt_configurations": {"status": "PENDING", "score": 0, "details": []},
            "structural_analysis": {"status": "PENDING", "score": 0, "details": []},
            "code_compliance": {"status": "PENDING", "score": 0, "details": []},
            "tekla_profile_mapping": {"status": "PENDING", "score": 0, "details": []}
        },
        "critical_missing_features": [],
        "recommendations": []
    }
    
    # Get raw members from input
    columns = input_data["members_raw"]["columns"]
    beams = input_data["members_raw"]["beams"]
    braces = input_data["members_raw"]["braces"]
    connections = input_data["connections_raw"]
    
    print(f"\n✅ MEMBER DATA ASSESSMENT")
    print("-" * 90)
    
    # 1. 3D Coordinates Assessment
    print("\n1️⃣  3D COORDINATES")
    coords_ok = 0
    for member in columns + beams + braces:
        if all(k in member for k in ["start_x", "start_y", "start_z", "end_x", "end_y", "end_z"]):
            coords_ok += 1
    
    coord_pct = (coords_ok / len(columns + beams + braces)) * 100 if (columns + beams + braces) else 0
    analysis["assessment"]["3d_coordinates"]["score"] = coord_pct
    analysis["assessment"]["3d_coordinates"]["status"] = "✅ READY" if coord_pct == 100 else ("⚠️  PARTIAL" if coord_pct > 50 else "❌ MISSING")
    print(f"   {analysis['assessment']['3d_coordinates']['status']}: {coords_ok}/{len(columns + beams + braces)} members have complete 3D coordinates ({coord_pct:.1f}%)")
    
    # 2. Member Properties
    print("\n2️⃣  MEMBER PROPERTIES")
    props_ok = 0
    for member in columns + beams + braces:
        if all(k in member for k in ["profile", "material", "length"]):
            props_ok += 1
    props_pct = (props_ok / len(columns + beams + braces)) * 100 if (columns + beams + braces) else 0
    analysis["assessment"]["member_properties"]["score"] = props_pct
    analysis["assessment"]["member_properties"]["status"] = "✅ READY" if props_pct == 100 else ("⚠️  PARTIAL" if props_pct > 50 else "❌ MISSING")
    print(f"   {analysis['assessment']['member_properties']['status']}: {props_ok}/{len(columns + beams + braces)} members have profile/material/length ({props_pct:.1f}%)")
    
    # 3. Member Orientations
    print("\n3️⃣  MEMBER ORIENTATION DATA")
    orient_ok = 0
    for member in columns + beams + braces:
        if "direction" in member or "rotation" in member:
            orient_ok += 1
    orient_pct = (orient_ok / len(columns + beams + braces)) * 100 if (columns + beams + braces) else 0
    analysis["assessment"]["tekla_profile_mapping"]["score"] = orient_pct
    print(f"   {('✅ READY' if orient_pct == 100 else ('⚠️  PARTIAL' if orient_pct > 50 else '❌ MISSING'))}: {orient_ok}/{len(columns + beams + braces)} members have orientation info ({orient_pct:.1f}%)")
    
    # 4. Connection Assessment
    print("\n4️⃣  CONNECTION DEFINITIONS")
    conn_ok = 0
    for conn in connections:
        if all(k in conn for k in ["type", "member1_id", "member2_id", "connection_x", "connection_y", "connection_z"]):
            conn_ok += 1
    conn_pct = (conn_ok / len(connections)) * 100 if connections else 0
    analysis["assessment"]["connection_definitions"]["score"] = conn_pct
    analysis["assessment"]["connection_definitions"]["status"] = "✅ READY" if conn_pct == 100 else ("⚠️  PARTIAL" if conn_pct > 50 else "❌ MISSING")
    print(f"   {analysis['assessment']['connection_definitions']['status']}: {conn_ok}/{len(connections)} connections have required properties ({conn_pct:.1f}%)")
    
    # 5. Weld Specifications
    print("\n5️⃣  WELD SPECIFICATIONS")
    weld_ok = 0
    for conn in connections:
        if "weld_type" in conn or "weld_size" in conn:
            weld_ok += 1
    weld_pct = (weld_ok / len(connections)) * 100 if connections else 0
    analysis["assessment"]["weld_specifications"]["score"] = weld_pct
    print(f"   {('✅ READY' if weld_pct == 100 else ('⚠️  PARTIAL' if weld_pct > 50 else '❌ MISSING'))}: {weld_ok}/{len(connections)} connections have weld specs ({weld_pct:.1f}%)")
    
    # 6. Bolt Configurations
    print("\n6️⃣  BOLT CONFIGURATIONS")
    bolt_ok = 0
    for conn in connections:
        if "bolt_config" in conn or "bolt_diameter" in conn:
            bolt_ok += 1
    bolt_pct = (bolt_ok / len(connections)) * 100 if connections else 0
    analysis["assessment"]["bolt_configurations"]["score"] = bolt_pct
    print(f"   {('✅ READY' if bolt_pct == 100 else ('⚠️  PARTIAL' if bolt_pct > 50 else '❌ MISSING'))}: {bolt_ok}/{len(connections)} connections have bolt specs ({bolt_pct:.1f}%)")
    
    # Calculate overall score
    overall_score = sum(a["score"] for a in analysis["assessment"].values()) / len(analysis["assessment"])
    
    print("\n" + "=" * 90)
    print(f"📊 OVERALL TEKLA READINESS SCORE: {overall_score:.1f}%")
    print("=" * 90)
    
    if overall_score >= 90:
        status = "🟢 PRODUCTION READY"
    elif overall_score >= 70:
        status = "🟡 NEEDS WORK"
    else:
        status = "🔴 SIGNIFICANT GAPS"
    
    print(f"{status}\n")
    
    # Identify critical missing features
    print("🚨 CRITICAL GAPS FOR TEKLA INTEGRATION:\n")
    
    if coord_pct < 100:
        analysis["critical_missing_features"].append("3D coordinate consistency across all members")
    if props_pct < 100:
        analysis["critical_missing_features"].append("Complete profile/material/length specifications")
    if orient_pct < 100:
        analysis["critical_missing_features"].append("Member orientation and rotation data")
    if conn_pct < 100:
        analysis["critical_missing_features"].append("Complete connection point coordinates (X,Y,Z)")
    if weld_pct < 100:
        analysis["critical_missing_features"].append("Weld specifications (size, type, process)")
    if bolt_pct < 100:
        analysis["critical_missing_features"].append("Bolt configuration (diameter, standard, spacing)")
    
    for i, gap in enumerate(analysis["critical_missing_features"], 1):
        print(f"  {i}. ❌ {gap}")
    
    # Generate recommendations
    print("\n📋 IMPLEMENTATION RECOMMENDATIONS:\n")
    
    recommendations = [
        {
            "priority": "CRITICAL",
            "action": "Enhance data enrichment layer",
            "description": "Create intermediate transformation that standardizes all member data to Tekla-ready format",
            "implementation": [
                "• Convert all members to standardized JSON schema with (start_x,y,z, end_x,y,z)",
                "• Add automatic rotation angle calculation from direction vectors",
                "• Map all profiles to Tekla profile library (W, HSS, etc.)",
                "• Validate material grades against ASTM standards"
            ]
        },
        {
            "priority": "CRITICAL",
            "action": "Implement connection 3D geometry generator",
            "description": "Automatically generate complete 3D connection geometry from beam-column intersections",
            "implementation": [
                "• Identify all member intersections (beam-column, brace-gusset)",
                "• Calculate connection point coordinates (X,Y,Z intersection)",
                "• Determine member end types (inside, outside, corner)",
                "• Generate weld fillet sizes from force transfer analysis"
            ]
        },
        {
            "priority": "HIGH",
            "action": "Add plate geometry standardization",
            "description": "Ensure all gusset/connection plates have complete dimensional data for Tekla",
            "implementation": [
                "• For each gusset plate: length, width, thickness",
                "• Add bolt hole pattern and spacing",
                "• Include corner radii and cutouts",
                "• Map to standard plate materials (A36, A572, etc.)"
            ]
        },
        {
            "priority": "HIGH",
            "action": "Create Tekla profile mapping module",
            "description": "Maintain master library of Tekla profile sizes for automatic mapping",
            "implementation": [
                "• Map AISC designations to Tekla native profiles",
                "• Handle special sections (HSS, tubes, angles)",
                "• Include material property lookups",
                "• Support metric and imperial units"
            ]
        },
        {
            "priority": "MEDIUM",
            "action": "Implement connection standardization",
            "description": "Categorize and standardize all connection types for Tekla import",
            "implementation": [
                "• Define connection types: Moment, ShearTab, EndPlate, Bolted, Welded",
                "• Generate bolt grids based on connection forces",
                "• Calculate weld penetration (PJP, CJP, Fillet)",
                "• Add connection capacity ratios for validation"
            ]
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        priority_icon = "🔴" if rec["priority"] == "CRITICAL" else ("🟡" if rec["priority"] == "HIGH" else "🟢")
        print(f"{i}. {priority_icon} {rec['priority']}: {rec['action']}")
        print(f"   {rec['description']}")
        for impl in rec["implementation"]:
            print(f"   {impl}")
        print()
        analysis["recommendations"].append(rec)
    
    # Save detailed analysis
    analysis_path = os.path.join(output_dir, "tekla_readiness_analysis.json")
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"✅ Detailed analysis saved to {analysis_path}\n")
    
    return analysis


def main():
    """Main entry point."""
    
    # Run pipeline with enriched data
    result, input_data, output_dir = run_enriched_pipeline_analysis()
    
    # Perform deep Tekla readiness analysis
    analysis = deep_tekla_readiness_analysis(result, input_data, output_dir)
    
    print("=" * 90)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 90)
    print(f"\nAll outputs saved to: {output_dir}")
    print("\nKey files:")
    print(f"  • prepared_input.json — Converted pipeline input")
    print(f"  • tekla_readiness_analysis.json — Full assessment")
    print(f"  • enriched_pipeline_result.json — Pipeline output")


if __name__ == "__main__":
    main()
