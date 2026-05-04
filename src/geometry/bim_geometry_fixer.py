#!/usr/bin/env python3
"""
BIM Geometry Fixer - Generalized BIM Geometry Repair for Tekla-to-JSON Pipeline
Handles DXF/IFC file truncation, unit intelligence, layer-based extraction, and coordinate precision.
"""

import json
import math
import re
import os
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path


class BIMGeometryFixer:
    """
    Generalized BIM Geometry Fixer for structural engineering models.
    Handles file truncation, unit conversion, layer extraction, and coordinate precision.
    """

    # DXF/IFC termination sequences
    DXF_TERMINATION = "  0\nEOF\n"
    IFC_TERMINATION = "ENDSEC;\nEND-ISO-10303-21;\n"

    # Unit conversion factors (to millimeters)
    UNIT_CONVERSIONS = {
        0: 1.0,      # Unitless (assume mm)
        1: 25.4,     # Inches to mm
        2: 304.8,    # Feet to mm
        3: 1609344.0,  # Miles to mm
        4: 1.0,      # Millimeters
        5: 10.0,     # Centimeters to mm
        6: 1000.0,   # Meters to mm
        7: 1000000.0,  # Kilometers to mm
    }

    # Target layers for structural extraction
    STRUCTURAL_LAYERS = {'COLUMNS', 'BEAMS', 'GRIDS'}

    # Coordinate snapping tolerance (0.5mm)
    SNAP_TOLERANCE = 0.5

    def __init__(self):
        self.node_map: Dict[Tuple[float, float, float], Tuple[float, float, float]] = {}
        self.processed_entities = 0
        self.fixed_issues = 0

    def fix_file(self, input_path: str, output_path: str) -> Dict[str, any]:
        """
        Main entry point for BIM geometry fixing.

        Args:
            input_path: Path to input DXF/IFC file
            output_path: Path to output fixed file

        Returns:
            Dictionary with processing statistics and fixes applied
        """
        print(f"🔧 BIM Geometry Fixer - Processing: {input_path}")

        # Determine file type
        file_ext = Path(input_path).suffix.lower()
        if file_ext == '.dxf':
            return self._fix_dxf_file(input_path, output_path)
        elif file_ext == '.ifc':
            return self._fix_ifc_file(input_path, output_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}. Only .dxf and .ifc supported.")

    def _fix_dxf_file(self, input_path: str, output_path: str) -> Dict[str, any]:
        """Fix DXF file with truncation, units, layers, and coordinates."""
        stats = {
            'file_type': 'DXF',
            'original_size': 0,
            'fixed_size': 0,
            'truncation_fixed': False,
            'units_converted': False,
            'layers_extracted': [],
            'coordinates_rounded': 0,
            'nodes_snapped': 0,
            'entities_processed': 0
        }

        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        stats['original_size'] = len(content)

        # 1. Fix file truncation
        if not content.strip().endswith('EOF'):
            content += self.DXF_TERMINATION
            stats['truncation_fixed'] = True
            self.fixed_issues += 1

        # 2. Parse and fix units
        content, units_fixed = self._fix_dxf_units(content)
        if units_fixed:
            stats['units_converted'] = True
            self.fixed_issues += 1

        # 3. Extract structural layers and fix coordinates
        content, layer_stats = self._extract_dxf_structural_layers(content)
        stats.update(layer_stats)

        # Ensure file ends with EOF if it was truncated
        if stats['truncation_fixed'] and not content.strip().endswith('EOF'):
            content += '\n  0\nEOF\n'

        # 4. Write fixed file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        stats['fixed_size'] = len(content)
        stats['entities_processed'] = self.processed_entities

        print(f"✅ DXF Fixed: {stats}")
        return stats

    def _fix_ifc_file(self, input_path: str, output_path: str) -> Dict[str, any]:
        """Fix IFC file with truncation and coordinate precision."""
        stats = {
            'file_type': 'IFC',
            'original_size': 0,
            'fixed_size': 0,
            'truncation_fixed': False,
            'coordinates_rounded': 0,
            'entities_processed': 0
        }

        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        stats['original_size'] = len(content)

        # 1. Fix file truncation
        if not content.strip().endswith('END-ISO-10303-21;'):
            content += self.IFC_TERMINATION
            stats['truncation_fixed'] = True
            self.fixed_issues += 1

        # 2. Fix coordinate precision in IFC
        content, coords_fixed = self._fix_ifc_coordinates(content)
        stats['coordinates_rounded'] = coords_fixed

        # 3. Write fixed file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        stats['fixed_size'] = len(content)
        stats['entities_processed'] = self.processed_entities

        print(f"✅ IFC Fixed: {stats}")
        return stats

    def _fix_dxf_units(self, content: str) -> Tuple[str, bool]:
        """Check and fix DXF units if coordinates don't match $INSUNITS setting."""
        lines = content.split('\n')
        units_fixed = False

        # Find $INSUNITS in HEADER section
        insunits_value = None
        in_header = False

        for i, line in enumerate(lines):
            line = line.strip()
            if line == 'SECTION' and i + 1 < len(lines) and lines[i + 1].strip() == '2' and i + 2 < len(lines) and lines[i + 2].strip() == 'HEADER':
                in_header = True
            elif line == 'ENDSEC' and in_header:
                in_header = False
            elif in_header and line == '9' and i + 1 < len(lines) and lines[i + 1].strip() == '$INSUNITS':
                # Look for the value after the $INSUNITS variable name and group code 70
                j = i + 2
                while j < len(lines) and j < i + 10:  # Look up to 10 lines ahead
                    if lines[j].strip() == '70' and j + 1 < len(lines):
                        try:
                            insunits_value = int(lines[j + 1].strip())
                            break
                        except ValueError:
                            pass
                    j += 1
                break

        # If units are meters (6) but coordinates are large (>100,000), scale to mm
        if insunits_value == 6:
            # Sample some coordinates to check scale - look in ENTITIES section
            coord_pattern = re.compile(r'^[\s]*1[0-5][\s]*$')
            large_coords_found = False

            in_entities = False
            for i, line in enumerate(lines):
                line = line.strip()
                if line == 'SECTION' and i + 2 < len(lines) and lines[i + 2].strip() == 'ENTITIES':
                    in_entities = True
                elif line == 'ENDSEC' and in_entities:
                    in_entities = False
                elif in_entities and coord_pattern.match(line) and i + 1 < len(lines):
                    try:
                        coord_value = float(lines[i + 1].strip())
                        if coord_value > 100000:  # Likely in meters but marked as such
                            large_coords_found = True
                            break
                    except ValueError:
                        continue

            if large_coords_found:
                print("🔄 Detected meter units with large coordinates - scaling to millimeters")
                # Scale all coordinates by 1000 (meters to mm) and update $INSUNITS to 4 (mm)
                lines = self._scale_dxf_coordinates(lines, 1000.0)

                # Update $INSUNITS to millimeters
                for i, line in enumerate(lines):
                    if line.strip() == '9' and i + 1 < len(lines) and lines[i + 1].strip() == '$INSUNITS':
                        if i + 2 < len(lines):
                            lines[i + 2] = '4'
                            units_fixed = True
                        break

        return '\n'.join(lines), units_fixed

    def _scale_dxf_coordinates(self, lines: List[str], scale_factor: float) -> List[str]:
        """Scale coordinate values in DXF by given factor."""
        coord_groups = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39']

        for i in range(len(lines)):
            line = lines[i].strip()
            if line in coord_groups and i + 1 < len(lines):
                try:
                    coord_value = float(lines[i + 1].strip())
                    lines[i + 1] = f"{coord_value * scale_factor:.4f}"
                except ValueError:
                    continue

        return lines

    def _extract_dxf_structural_layers(self, content: str) -> Tuple[str, Dict[str, any]]:
        """Extract only COLUMNS, BEAMS, and GRIDS layers from DXF."""
        lines = content.split('\n')
        filtered_lines = []
        current_entity_lines = []
        in_entity = False
        entity_layer = None
        in_entities_section = False
        stats = {
            'layers_extracted': [],
            'coordinates_rounded': 0,
            'nodes_snapped': 0
        }

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Track if we're in ENTITIES section
            if line == 'SECTION' and i + 2 < len(lines) and lines[i + 2].strip() == 'ENTITIES':
                in_entities_section = True
                filtered_lines.append(lines[i])
                filtered_lines.append(lines[i + 1])
                filtered_lines.append(lines[i + 2])
                i += 3
                continue
            elif line == 'ENDSEC' and in_entities_section:
                in_entities_section = False
                # Add any remaining entity
                if in_entity and entity_layer in self.STRUCTURAL_LAYERS:
                    processed_lines, coord_stats = self._process_dxf_entity_coordinates(current_entity_lines)
                    filtered_lines.extend(processed_lines)
                    stats['coordinates_rounded'] += coord_stats['rounded']
                    stats['nodes_snapped'] += coord_stats['snapped']
                    stats['layers_extracted'].append(entity_layer)
                    self.processed_entities += 1
                filtered_lines.append(lines[i])
                i += 1
                continue

            if not in_entities_section:
                # Keep all non-ENTITIES sections as-is
                filtered_lines.append(lines[i])
                i += 1
                continue

            # In ENTITIES section - handle entities
            if line == '0':
                # Check what follows this '0'
                next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''

                if next_line == 'ENDSEC':
                    # End of ENTITIES section - add any remaining entity and the ENDSEC
                    if in_entity and entity_layer in self.STRUCTURAL_LAYERS:
                        processed_lines, coord_stats = self._process_dxf_entity_coordinates(current_entity_lines)
                        filtered_lines.extend(processed_lines)
                        stats['coordinates_rounded'] += coord_stats['rounded']
                        stats['nodes_snapped'] += coord_stats['snapped']
                        stats['layers_extracted'].append(entity_layer)
                        self.processed_entities += 1
                    filtered_lines.append(lines[i])  # '0'
                    filtered_lines.append(lines[i + 1])  # 'ENDSEC'
                    in_entities_section = False
                    i += 2
                    continue
                elif next_line == 'EOF':
                    # End of file
                    filtered_lines.append(lines[i])  # '0'
                    filtered_lines.append(lines[i + 1])  # 'EOF'
                    i += 2
                    continue
                else:
                    # Start of new entity
                    if in_entity:
                        if entity_layer in self.STRUCTURAL_LAYERS:
                            processed_lines, coord_stats = self._process_dxf_entity_coordinates(current_entity_lines)
                            filtered_lines.extend(processed_lines)
                            stats['coordinates_rounded'] += coord_stats['rounded']
                            stats['nodes_snapped'] += coord_stats['snapped']
                            stats['layers_extracted'].append(entity_layer)
                            self.processed_entities += 1

                    # Start new entity
                    current_entity_lines = [lines[i]]  # Keep the '0'
                    in_entity = True
                    entity_layer = None

                    # Look ahead for layer (group code 8)
                    j = i + 1
                    while j < len(lines) and j < i + 20:  # Look up to 20 lines ahead
                        if lines[j].strip() == '8' and j + 1 < len(lines):
                            entity_layer = lines[j + 1].strip()
                            break
                        j += 1  # Check every line

            elif in_entity:
                current_entity_lines.append(lines[i])

            i += 1

        # Remove duplicates from layers_extracted
        stats['layers_extracted'] = list(set(stats['layers_extracted']))

        return '\n'.join(filtered_lines), stats

    def _process_dxf_entity_coordinates(self, entity_lines: List[str]) -> Tuple[List[str], Dict[str, int]]:
        """Process coordinates in a DXF entity: round to 4 decimals and snap nodes."""
        coord_groups = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39']
        stats = {'rounded': 0, 'snapped': 0}

        for i in range(len(entity_lines)):
            line = entity_lines[i].strip()
            if line in coord_groups and i + 1 < len(entity_lines):
                try:
                    coord_value = float(entity_lines[i + 1].strip())
                    # Round to 4 decimal places
                    rounded_value = round(coord_value, 4)
                    if rounded_value != coord_value:
                        stats['rounded'] += 1
                    entity_lines[i + 1] = f"{rounded_value:.4f}"

                    # For 3D coordinates (groups 10-12, 11-13, etc.), check for snapping
                    if line in ['10', '11', '12', '13']:
                        # This is a coordinate triplet - collect all three values
                        x = rounded_value
                        y = z = 0.0

                        # Get Y coordinate (next group)
                        if i + 3 < len(entity_lines) and entity_lines[i + 2].strip() in ['20', '21', '22', '23']:
                            try:
                                y = round(float(entity_lines[i + 3].strip()), 4)
                                entity_lines[i + 3] = f"{y:.4f}"
                            except ValueError:
                                pass

                        # Get Z coordinate (next group)
                        if i + 5 < len(entity_lines) and entity_lines[i + 4].strip() in ['30', '31', '32', '33']:
                            try:
                                z = round(float(entity_lines[i + 5].strip()), 4)
                                entity_lines[i + 5] = f"{z:.4f}"
                            except ValueError:
                                pass

                        # Snap to existing node if within tolerance
                        snapped_point = self._snap_to_node((x, y, z))
                        if snapped_point != (x, y, z):
                            stats['snapped'] += 1
                            entity_lines[i + 1] = f"{snapped_point[0]:.4f}"
                            if i + 3 < len(entity_lines):
                                entity_lines[i + 3] = f"{snapped_point[1]:.4f}"
                            if i + 5 < len(entity_lines):
                                entity_lines[i + 5] = f"{snapped_point[2]:.4f}"

                except ValueError:
                    continue

        return entity_lines, stats

    def _snap_to_node(self, point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Snap point to existing node if within tolerance."""
        for existing_point in self.node_map.keys():
            distance = math.sqrt(
                (point[0] - existing_point[0]) ** 2 +
                (point[1] - existing_point[1]) ** 2 +
                (point[2] - existing_point[2]) ** 2
            )
            if distance <= self.SNAP_TOLERANCE:
                return existing_point

        # No nearby node found, add this as new node
        self.node_map[point] = point
        return point

    def _fix_ifc_coordinates(self, content: str) -> Tuple[str, int]:
        """Fix coordinate precision in IFC file."""
        # IFC coordinate patterns - look for CartesianPoint coordinates
        coord_pattern = re.compile(r'#\d+\s*=\s*IFCCARTESIANPOINT\s*\(\s*\(([^)]+)\)\s*\)\s*;')
        coords_fixed = 0

        def fix_coords(match):
            nonlocal coords_fixed
            coords_str = match.group(1)
            # Split coordinates and round each to 4 decimals
            coords = []
            for coord in coords_str.split(','):
                try:
                    value = float(coord.strip())
                    rounded = round(value, 4)
                    if rounded != value:
                        coords_fixed += 1
                    coords.append(f"{rounded:.4f}")
                except ValueError:
                    coords.append(coord.strip())

            return match.group(0).replace(coords_str, ', '.join(coords))

        content = coord_pattern.sub(fix_coords, content)
        return content, coords_fixed


def main():
    """Command line interface for BIM Geometry Fixer."""
    import argparse

    parser = argparse.ArgumentParser(description='BIM Geometry Fixer - Fix DXF/IFC files for structural engineering')
    parser.add_argument('input', help='Input DXF or IFC file')
    parser.add_argument('output', help='Output fixed file')
    parser.add_argument('--json-report', help='Output JSON report file')

    args = parser.parse_args()

    fixer = BIMGeometryFixer()

    try:
        stats = fixer.fix_file(args.input, args.output)

        if args.json_report:
            with open(args.json_report, 'w') as f:
                json.dump(stats, f, indent=2)
            print(f"📊 Report saved to: {args.json_report}")

        print("🎉 BIM Geometry Fixer completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())