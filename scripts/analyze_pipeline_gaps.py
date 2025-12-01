#!/usr/bin/env python3
"""
Run complex structure through full pipeline and analyze output for Tekla integration.
"""

import sys
import json
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, "/Users/sahil/Documents/aibuildx")

from src.pipeline.pipeline_compat import run_pipeline

def run_deep_analysis():
    """Run complex structure through entire pipeline."""
    
    input_json_path = "/Users/sahil/Documents/aibuildx/examples/complex_structure_input.json"
    output_dir = "/Users/sahil/Documents/aibuildx/examples/pipeline_analysis"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("🔬 DEEP PIPELINE ANALYSIS: Complex 3-Story Building")
    print("=" * 80)
    
    # Load input
    print("\n📥 Loading input structure...")
    with open(input_json_path) as f:
        input_data = json.load(f)
    
    print(f"   ✓ Building: {input_data['building']['name']}")
    print(f"   ✓ Dimensions: {input_data['building']['width']}m x {input_data['building']['length']}m x {input_data['building']['height']}m")
    print(f"   ✓ Members: {input_data['summary']['total_members']}")
    print(f"   ✓ Connections: {input_data['summary']['total_connections']}")
    
    # Run pipeline
    print("\n🔄 Running full pipeline (17 agents)...")
    try:
        result = run_pipeline(input_json_path, out_dir=output_dir)
        print("   ✓ Pipeline execution complete!")
    except Exception as e:
        print(f"   ✗ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Save result
    result_path = os.path.join(output_dir, "pipeline_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"   ✓ Result saved to {result_path}")
    
    return result, input_data, output_dir


def analyze_gaps(result, input_data, output_dir):
    """Deep analysis of missing properties for Tekla 3D rendering."""
    
    print("\n" + "=" * 80)
    print("🔍 GAP ANALYSIS: Tekla 3D Rendering Requirements")
    print("=" * 80)
    
    gaps = {
        "3D_coordinates": {"found": 0, "missing": 0, "issues": []},
        "rotations": {"found": 0, "missing": 0, "issues": []},
        "connection_details": {"found": 0, "missing": 0, "issues": []},
        "plate_geometry": {"found": 0, "missing": 0, "issues": []},
        "material_specs": {"found": 0, "missing": 0, "issues": []},
        "weld_specs": {"found": 0, "missing": 0, "issues": []},
        "bolt_specifications": {"found": 0, "missing": 0, "issues": []},
        "end_connections": {"found": 0, "missing": 0, "issues": []},
        "member_orientations": {"found": 0, "missing": 0, "issues": []},
        "profile_references": {"found": 0, "missing": 0, "issues": []}
    }
    
    # Extract member data from result
    if "engineer" in result and "members" in result["engineer"]:
        members = result["engineer"]["members"]
        
        print(f"\n📋 Analyzing {len(members)} members...")
        
        for member in members:
            member_id = member.get("id", "UNKNOWN")
            
            # 1. Check 3D coordinates
            has_3d = all(k in member for k in ["start_x", "start_y", "start_z", "end_x", "end_y", "end_z"])
            if has_3d:
                gaps["3D_coordinates"]["found"] += 1
            else:
                gaps["3D_coordinates"]["missing"] += 1
                gaps["3D_coordinates"]["issues"].append(member_id)
            
            # 2. Check rotations
            has_rotation = "rotation" in member or "rotation_angle" in member
            if has_rotation:
                gaps["rotations"]["found"] += 1
            else:
                gaps["rotations"]["missing"] += 1
                gaps["rotations"]["issues"].append(member_id)
            
            # 3. Check member orientation
            has_orientation = "direction" in member or "axis" in member
            if has_orientation:
                gaps["member_orientations"]["found"] += 1
            else:
                gaps["member_orientations"]["missing"] += 1
                gaps["member_orientations"]["issues"].append(member_id)
            
            # 4. Check profile reference
            has_profile = "profile" in member or "section" in member
            if has_profile:
                gaps["profile_references"]["found"] += 1
            else:
                gaps["profile_references"]["missing"] += 1
                gaps["profile_references"]["issues"].append(member_id)
            
            # 5. Check material specs
            has_material = "material" in member or "yield_strength" in member
            if has_material:
                gaps["material_specs"]["found"] += 1
            else:
                gaps["material_specs"]["missing"] += 1
                gaps["material_specs"]["issues"].append(member_id)
    
    # Analyze connections
    if "connections" in result:
        connections = result.get("connections", {})
        conn_list = connections.get("connections", []) if isinstance(connections, dict) else connections
        
        print(f"\n🔗 Analyzing {len(conn_list)} connections...")
        
        for conn in conn_list:
            conn_id = conn.get("id", "UNKNOWN")
            
            # Check connection details
            has_details = all(k in conn for k in ["type", "member1_id", "member2_id"])
            if has_details:
                gaps["connection_details"]["found"] += 1
            else:
                gaps["connection_details"]["missing"] += 1
                gaps["connection_details"]["issues"].append(conn_id)
            
            # Check weld specs
            has_weld = "weld_type" in conn or "fillet_size" in conn
            if has_weld:
                gaps["weld_specs"]["found"] += 1
            else:
                gaps["weld_specs"]["missing"] += 1
                gaps["weld_specs"]["issues"].append(conn_id)
            
            # Check bolt specs
            has_bolts = "bolt_diameter" in conn or "bolt_config" in conn
            if has_bolts:
                gaps["bolt_specifications"]["found"] += 1
            else:
                gaps["bolt_specifications"]["missing"] += 1
                gaps["bolt_specifications"]["issues"].append(conn_id)
            
            # Check connection coordinates
            has_coords = all(k in conn for k in ["connection_x", "connection_y", "connection_z"])
            if has_coords:
                gaps["end_connections"]["found"] += 1
            else:
                gaps["end_connections"]["missing"] += 1
                gaps["end_connections"]["issues"].append(conn_id)
    
    # Analyze plates
    if "fabrication" in result and "plates" in result["fabrication"]:
        plates = result["fabrication"]["plates"]
        
        print(f"\n📦 Analyzing {len(plates)} plates...")
        
        for plate in plates:
            plate_id = plate.get("id", "UNKNOWN")
            
            # Check plate geometry
            has_geom = all(k in plate for k in ["thickness", "length", "width"])
            if has_geom:
                gaps["plate_geometry"]["found"] += 1
            else:
                gaps["plate_geometry"]["missing"] += 1
                gaps["plate_geometry"]["issues"].append(plate_id)
            
            # Check coordinates
            has_coords = all(k in plate for k in ["connection_x", "connection_y", "connection_z"])
            if has_coords:
                gaps["end_connections"]["found"] += 1
            else:
                gaps["end_connections"]["missing"] += 1
                gaps["end_connections"]["issues"].append(plate_id)
    
    # Print gap analysis results
    print("\n" + "-" * 80)
    print("📊 GAP ANALYSIS RESULTS:")
    print("-" * 80)
    
    total_found = 0
    total_missing = 0
    critical_gaps = []
    
    for category, stats in sorted(gaps.items()):
        total = stats["found"] + stats["missing"]
        if total == 0:
            continue
        
        pct = (stats["found"] / total * 100) if total > 0 else 0
        status = "✅" if pct == 100 else ("⚠️ " if pct >= 80 else "❌")
        
        print(f"\n{status} {category.replace('_', ' ').upper()}")
        print(f"   Found: {stats['found']}/{total} ({pct:.1f}%)")
        
        if stats["issues"]:
            if len(stats["issues"]) <= 5:
                print(f"   Missing in: {', '.join(stats['issues'][:5])}")
            else:
                print(f"   Missing in: {', '.join(stats['issues'][:5])} ... +{len(stats['issues'])-5} more")
            critical_gaps.append(category)
        
        total_found += stats["found"]
        total_missing += stats["missing"]
    
    print("\n" + "=" * 80)
    print(f"📈 OVERALL: {total_found}/{total_found + total_missing} ({total_found/(total_found+total_missing)*100:.1f}%) ready for Tekla")
    print("=" * 80)
    
    if critical_gaps:
        print(f"\n🚨 CRITICAL GAPS IDENTIFIED ({len(critical_gaps)}):")
        for gap in critical_gaps:
            print(f"   ❌ {gap}")
    
    return gaps


def generate_recommendations(gaps):
    """Generate implementation recommendations."""
    
    print("\n" + "=" * 80)
    print("📋 IMPLEMENTATION RECOMMENDATIONS FOR TEKLA INTEGRATION")
    print("=" * 80)
    
    recommendations = []
    
    if gaps["3D_coordinates"]["missing"] > 0:
        recommendations.append({
            "priority": "CRITICAL",
            "category": "3D Coordinates",
            "issue": f"{gaps['3D_coordinates']['missing']} members missing (X,Y,Z) coordinates",
            "solution": "Enhance miner agent to extract/normalize 2D→3D coordinate conversion with Z coordinate tracking per story",
            "implementation": [
                "1. Add Z coordinate calculation based on story level",
                "2. Verify start/end points for all member types",
                "3. Add coordinate validation in validator agent"
            ]
        })
    
    if gaps["rotations"]["missing"] > 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Member Rotations",
            "issue": f"{gaps['rotations']['missing']} members missing rotation angles",
            "solution": "Add rotation angle computation for non-orthogonal members (braces, skew beams)",
            "implementation": [
                "1. Calculate rotation from direction vector (start→end)",
                "2. Support 0°, 90°, 180°, 270° for orthogonal + diagonal angles",
                "3. Store as 'rotation_angle' in degrees"
            ]
        })
    
    if gaps["connection_details"]["missing"] > 0:
        recommendations.append({
            "priority": "CRITICAL",
            "category": "Connection Details",
            "issue": f"{gaps['connection_details']['missing']} connections missing detail specs",
            "solution": "Enhance connection designer to produce complete Tekla-ready connection objects",
            "implementation": [
                "1. Map connection type to Tekla connection class (Moment, SimpleShear, EndPlate, etc.)",
                "2. Determine member end types (beam end, column end, brace end)",
                "3. Calculate connection point coordinates (3D)"
            ]
        })
    
    if gaps["weld_specs"]["missing"] > 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Weld Specifications",
            "issue": f"{gaps['weld_specs']['missing']} connections missing weld details",
            "solution": "Add weld size, type, and penetration specifications from connection designer",
            "implementation": [
                "1. Calculate fillet weld size from force transfer requirements",
                "2. Specify weld type: FILLET, GROOVE, PJP, CJP",
                "3. Add weld code (AWS D1.1) compliance checking"
            ]
        })
    
    if gaps["bolt_specifications"]["missing"] > 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Bolt Specifications",
            "issue": f"{gaps['bolt_specifications']['missing']} connections missing bolt details",
            "solution": "Add bolt configuration (standard, diameter, quantity, spacing) from connection designer",
            "implementation": [
                "1. Specify bolt standard (ASTM A325, A490, etc.)",
                "2. Calculate bolt diameter and grid from connection forces",
                "3. Define bolt spacing (3d_bolt for typical)",
                "4. Add edge distances and clearances"
            ]
        })
    
    if gaps["plate_geometry"]["missing"] > 0:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Plate Geometry",
            "issue": f"{gaps['plate_geometry']['missing']} plates missing dimensional data",
            "solution": "Ensure fabrication agent produces complete plate definitions",
            "implementation": [
                "1. Include thickness, length, width for all plates",
                "2. Add corner radii and bolt hole patterns",
                "3. Specify material grade and finish",
                "4. Include plate rotation/orientation"
            ]
        })
    
    if gaps["end_connections"]["missing"] > 0:
        recommendations.append({
            "priority": "CRITICAL",
            "category": "End Connection Coordinates",
            "issue": f"{gaps['end_connections']['missing']} members/connections missing 3D positions",
            "solution": "Add 3D positioning for all connection points and member ends",
            "implementation": [
                "1. Calculate member end coordinates (start_x, start_y, start_z, end_x, end_y, end_z)",
                "2. Store connection point as (connection_x, connection_y, connection_z)",
                "3. Validate no out-of-bounds coordinates"
            ]
        })
    
    if gaps["member_orientations"]["missing"] > 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Member Orientation",
            "issue": f"{gaps['member_orientations']['missing']} members missing orientation info",
            "solution": "Add orientation vectors or direction labels (X, Y, Z, DIAGONAL, etc.)",
            "implementation": [
                "1. Add 'direction' field: 'X', 'Y', 'Z', 'DIAGONAL'",
                "2. Calculate direction vector from endpoints",
                "3. Add 'horizontal', 'vertical', 'sloped' classification"
            ]
        })
    
    if gaps["material_specs"]["missing"] > 0:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Material Specifications",
            "issue": f"{gaps['material_specs']['missing']} members missing material data",
            "solution": "Ensure all members have material grade, yield strength, and properties",
            "implementation": [
                "1. Add standard grades: A992, A500, A36, etc.",
                "2. Include yield strength (MPa or ksi)",
                "3. Add ultimate tensile strength",
                "4. Include density for weight calculations"
            ]
        })
    
    print()
    for i, rec in enumerate(recommendations, 1):
        priority_color = "🔴" if rec["priority"] == "CRITICAL" else ("🟡" if rec["priority"] == "HIGH" else "🟢")
        print(f"\n{i}. {priority_color} {rec['priority']}: {rec['category']}")
        print(f"   Issue: {rec['issue']}")
        print(f"   Solution: {rec['solution']}")
        print(f"   Implementation Steps:")
        for step in rec["implementation"]:
            print(f"      {step}")
    
    return recommendations


def main():
    """Main entry point."""
    
    # Run pipeline
    result, input_data, output_dir = run_deep_analysis()
    
    if result is None:
        print("\n❌ Pipeline failed. Exiting.")
        return
    
    # Analyze gaps
    gaps = analyze_gaps(result, input_data, output_dir)
    
    # Generate recommendations
    recommendations = generate_recommendations(gaps)
    
    # Save gap analysis
    gap_report = {
        "timestamp": "2025-12-01",
        "structure": input_data["building"]["name"],
        "members": input_data["summary"]["total_members"],
        "gaps": gaps,
        "recommendations": [
            {
                "priority": r["priority"],
                "category": r["category"],
                "issue": r["issue"],
                "solution": r["solution"]
            }
            for r in recommendations
        ]
    }
    
    gap_report_path = os.path.join(output_dir, "gap_analysis_report.json")
    with open(gap_report_path, "w") as f:
        json.dump(gap_report, f, indent=2)
    print(f"\n✅ Gap analysis report saved to {gap_report_path}")


if __name__ == "__main__":
    main()
