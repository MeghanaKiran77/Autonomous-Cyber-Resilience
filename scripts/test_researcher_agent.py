#!/usr/bin/env python3
"""
Test script for Researcher Agent.

Usage:
    export GROQ_API_KEY=your-key-here
    python scripts/test_researcher_agent.py
"""

import sys
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.researcher import analyze_target


def test_researcher():
    """Test Researcher Agent with mock target data."""
    print("=" * 60)
    print("Testing Researcher Agent")
    print("=" * 60)

    # Mock target spec
    target_spec = {
        "type": "sqli",
        "name": "flask_sqli_demo",
        "port": 5000,
        "path": "targets/flask_sqli_demo/app.py",
    }

    # Mock recon data
    recon_data = {
        "/": {
            "status": 200,
            "body_preview": '{"message": "Flask SQLi Demo"}',
        },
        "/health": {
            "status": 200,
            "body_preview": "OK",
        },
        "/search?q=test": {
            "status": 200,
            "body_preview": '{"results": [{"id": 2, "name": "apple"}]}',
        },
    }

    # Create temp run folder
    with tempfile.TemporaryDirectory() as tmpdir:
        run_folder = Path(tmpdir)

        print("\nTarget:", target_spec["name"])
        print("Type:", target_spec["type"])
        print("\nCalling Researcher Agent...")
        print("(This may take 10-30 seconds)")
        print()

        try:
            findings = analyze_target(target_spec, recon_data, run_folder)

            print("✓ Researcher Agent completed")
            print(f"\nFindings: {len(findings.get('findings', []))}")
            
            for i, finding in enumerate(findings.get("findings", []), 1):
                print(f"\n  Finding {i}:")
                print(f"    Endpoint: {finding.get('endpoint')}")
                print(f"    Parameter: {finding.get('parameter')}")
                print(f"    Type: {finding.get('vulnerability_type')}")
                print(f"    Confidence: {finding.get('confidence')}")
                print(f"    Reasoning: {finding.get('reasoning', '')[:100]}...")

            # Check if findings.json was created
            findings_file = run_folder / "findings.json"
            if findings_file.exists():
                print(f"\n✓ findings.json created ({findings_file.stat().st_size} bytes)")
            else:
                print("\n✗ findings.json not created")

            print("\n" + "=" * 60)
            print("✓ Test passed!")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = test_researcher()
    sys.exit(0 if success else 1)
