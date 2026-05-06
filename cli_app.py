
#!/usr/bin/env python3
"""
Company Contact Finder - Command Line Interface
Usage: python cli_app.py input.csv output.csv
"""

import sys
import argparse
import pandas as pd
from datetime import datetime
from contact_finder import ContactFinder

def main():
    parser = argparse.ArgumentParser(description='Find company contact information from CSV')
    parser.add_argument('input_csv', help='Input CSV file path')
    parser.add_argument('output_csv', nargs='?', help='Output CSV file path (optional)')
    parser.add_argument('--limit', type=int, default=50, help='Maximum number of companies to process (default: 50)')

    args = parser.parse_args()

    # Generate output filename if not provided
    if not args.output_csv:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_csv = f"company_contacts_{timestamp}.csv"

    try:
        # Load input CSV
        print(f"📂 Loading CSV file: {args.input_csv}")
        df = pd.read_csv(args.input_csv)
        print(f"✅ Loaded {len(df)} companies")

        # Validate required columns
        if 'company_name' not in df.columns:
            print("❌ Error: 'company_name' column is required")
            sys.exit(1)

        # Limit processing for safety
        if len(df) > args.limit:
            print(f"⚠️  Limiting to first {args.limit} companies for safety")
            df = df.head(args.limit)

        # Initialize contact finder
        print("🔧 Initializing contact finder...")
        finder = ContactFinder()

        # Process companies
        print("🔍 Starting contact search...")
        result_df = finder.process_csv(df)

        # Save results
        result_df.to_csv(args.output_csv, index=False)
        print(f"💾 Results saved to: {args.output_csv}")

        # Summary
        found_count = len(result_df[result_df['phone_number'] != 'Not Available'])
        success_rate = (found_count / len(result_df)) * 100

        print("\n📊 Summary:")
        print(f"  Total companies: {len(result_df)}")
        print(f"  Contacts found: {found_count}")
        print(f"  Success rate: {success_rate:.1f}%")

        # Show confidence breakdown
        if 'confidence' in result_df.columns:
            conf_counts = result_df['confidence'].value_counts()
            print("\n🎯 Confidence breakdown:")
            for conf, count in conf_counts.items():
                print(f"  {conf}: {count}")

    except FileNotFoundError:
        print(f"❌ Error: File '{args.input_csv}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
