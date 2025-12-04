#!/usr/bin/env python3
"""
CLI tool for DWG→Tekla conversion pipeline.
Provides command-line interface to run the full conversion workflow.

Usage:
    python cli.py convert --input input.dwg --output outputs/model.ifc
    python cli.py web --host 0.0.0.0 --port 5000
    python cli.py validate --input model.json
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.pipeline_compat import run_pipeline
from src.pipeline.miner import extract_from_dxf, extract_from_ifc


class ConversionCLI:
    """Command-line interface for the conversion pipeline."""

    @staticmethod
    def convert(input_file: str, output_dir: str = "outputs", format: str = "ifc", verbose: bool = False) -> int:
        """Convert DWG/DXF to Tekla model (IFC/JSON)."""
        print(f"🔄 Converting {input_file}...")
        
        if not os.path.exists(input_file):
            print(f"❌ Error: Input file '{input_file}' not found")
            return 1
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Run pipeline
            result = run_pipeline(input_file, out_dir=output_dir)
            # Backwards-compatible: if the pipeline returned a raw list of members,
            # wrap it into a dict so callers relying on dict semantics continue to work.
            if isinstance(result, list):
                result = {'miner': result}
            
            if isinstance(result, dict) and result.get('status') == 'error':
                print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
                return 1
            
            # Extract statistics (be tolerant of legacy shapes)
            miner_section = result.get('miner', {})
            if isinstance(miner_section, list):
                members = miner_section
            else:
                members = miner_section.get('members', []) if isinstance(miner_section, dict) else []

            validator_section = result.get('validator', {})
            errors = validator_section.get('errors', []) if isinstance(validator_section, dict) else []

            clashes_section = result.get('clashes', {})
            clashes = clashes_section.get('clashes', []) if isinstance(clashes_section, dict) else []
            
            # Print summary
            print(f"✅ Conversion completed!")
            print(f"   Members: {len(members)}")
            print(f"   Errors: {len(errors)}")
            print(f"   Clashes: {len(clashes)}")
            print(f"   Output: {output_dir}/")
            
            # List output files
            if os.path.exists(output_dir):
                files = [f for f in os.listdir(output_dir) if f.endswith(('.json', '.ifc', '.csv'))]
                for f in files:
                    size = os.path.getsize(os.path.join(output_dir, f)) / 1024
                    print(f"   - {f} ({size:.1f} KB)")

            # If IFC exists, print viewer URL hint
            if os.path.exists(os.path.join(output_dir, 'model.ifc')):
                job_id_from_dir = os.path.basename(output_dir)
                viewer_url = f"/viewer/{job_id_from_dir}"
                print(f"\n👁  3D Viewer: Open http://localhost:5001{viewer_url}")
            
            if verbose:
                print(f"\n📊 Full result keys: {list(result.keys())}")
            
            return 0
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if verbose:
                import traceback
                traceback.print_exc()
            return 1

    @staticmethod
    def validate(input_file: str, verbose: bool = False) -> int:
        """Validate a pipeline output JSON file."""
        print(f"🔍 Validating {input_file}...")
        
        if not os.path.exists(input_file):
            print(f"❌ Error: Input file '{input_file}' not found")
            return 1
        
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Basic validation
            errors = []
            warnings = []
            
            if not isinstance(data, dict):
                errors.append("Root must be a dictionary")
            
            # Check for required keys
            for key in ['miner', 'engineer', 'validator']:
                if key not in data:
                    warnings.append(f"Missing key: {key}")
            
            # Check members
            members = data.get('miner', {}).get('members', [])
            if not members:
                warnings.append("No members found")
            else:
                for i, m in enumerate(members):
                    if not m.get('id'):
                        errors.append(f"Member {i} missing 'id'")
                    if not m.get('start') or not m.get('end'):
                        errors.append(f"Member {i} missing geometry (start/end)")
            
            # Report
            print(f"✅ Validation complete")
            if errors:
                print(f"❌ Errors: {len(errors)}")
                for err in errors[:5]:
                    print(f"   - {err}")
            if warnings:
                print(f"⚠️  Warnings: {len(warnings)}")
                for warn in warnings[:5]:
                    print(f"   - {warn}")
            
            return 0 if not errors else 1
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if verbose:
                import traceback
                traceback.print_exc()
            return 1

    @staticmethod
    def web(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> int:
        """Launch the web UI."""
        print(f"🌐 Starting web server on {host}:{port}...")
        try:
            from app import app
            app.run(host=host, port=port, debug=debug)
            return 0
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1

    @staticmethod
    def batch(config_file: str, verbose: bool = False) -> int:
        """Run batch conversion from a configuration file."""
        print(f"📦 Running batch conversion from {config_file}...")
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            jobs = config.get('jobs', [])
            results = []
            
            for i, job in enumerate(jobs, 1):
                input_file = job.get('input')
                output_dir = job.get('output', f'outputs/job_{i}')
                
                print(f"\n[{i}/{len(jobs)}] Processing {input_file}...")
                ret = ConversionCLI.convert(input_file, output_dir, verbose=verbose)
                results.append({'input': input_file, 'success': ret == 0})
            
            print(f"\n📊 Batch complete: {sum(1 for r in results if r['success'])}/{len(results)} succeeded")
            return 0
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description='DWG→Tekla Conversion Pipeline CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  %(prog)s convert --input drawing.dwg --output ./model
  %(prog)s validate --input output/final.json
  %(prog)s web --port 8080
  %(prog)s batch --config jobs.json
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert DWG/DXF to Tekla model')
    convert_parser.add_argument('--input', '-i', required=True, help='Input DWG/DXF file')
    convert_parser.add_argument('--output', '-o', default='outputs', help='Output directory')
    convert_parser.add_argument('--format', '-f', choices=['ifc', 'json'], default='ifc', help='Output format')
    convert_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate pipeline output')
    validate_parser.add_argument('--input', '-i', required=True, help='Input JSON file')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Launch web UI')
    web_parser.add_argument('--host', default='0.0.0.0', help='Bind address')
    web_parser.add_argument('--port', '-p', type=int, default=5000, help='Port number')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Run batch conversion')
    batch_parser.add_argument('--config', '-c', required=True, help='Configuration JSON file')
    batch_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'convert':
        return ConversionCLI.convert(args.input, args.output, args.format, args.verbose)
    elif args.command == 'validate':
        return ConversionCLI.validate(args.input, args.verbose)
    elif args.command == 'web':
        return ConversionCLI.web(args.host, args.port, args.debug)
    elif args.command == 'batch':
        return ConversionCLI.batch(args.config, args.verbose)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
