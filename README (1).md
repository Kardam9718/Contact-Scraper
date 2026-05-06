# Company Contact Finder Tool

A Python-based tool to extract publicly available phone numbers for companies from CSV data using web scraping and search techniques.

## 🚀 Features

- **CSV Processing**: Upload CSV with company information
- **Multi-source Search**: Google search, company websites, business directories
- **Phone Extraction**: Indian phone number patterns with validation
- **Confidence Scoring**: High/Medium/Low confidence levels
- **Rate Limiting**: Built-in delays to respect website policies
- **Multiple Interfaces**: Streamlit web app + CLI tool
- **Progress Tracking**: Real-time processing updates

## 📋 Requirements

- Python 3.8+
- Internet connection
- CSV file with company data

## 🛠️ Installation

1. **Clone/Download the files**
   ```bash
   # Download all files to a directory
   mkdir company-contact-finder
   cd company-contact-finder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python -c "import streamlit, pandas, requests, bs4; print('✅ All dependencies installed')"
   ```

## 📊 CSV Format

### Required Columns:
- `company_name` (string, required)

### Optional Columns:
- `director_name` (string, optional)
- `cin` (string, optional)

### Example CSV:
```csv
company_name,director_name,cin
Tata Consultancy Services,Rajesh Gopinathan,L72900MH1995PLC084781
Infosys Limited,Salil Parekh,L85110KA1981PLC013115
Reliance Industries,Mukesh Ambani,L17110MH1973PLC019786
```

## 🖥️ Usage

### Option 1: Streamlit Web App (Recommended)

```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Drag & drop CSV upload
- Real-time progress tracking
- Live results display
- Download processed CSV
- Sample CSV generator

### Option 2: Command Line Interface

```bash
# Basic usage
python cli_app.py input.csv

# Specify output file
python cli_app.py input.csv output.csv

# Limit processing (default: 50)
python cli_app.py input.csv --limit 10
```

### Option 3: Python Script Integration

```python
from contact_finder import ContactFinder
import pandas as pd

# Load your data
df = pd.read_csv('companies.csv')

# Initialize finder
finder = ContactFinder()

# Process companies
result_df = finder.process_csv(df)

# Save results
result_df.to_csv('results.csv', index=False)
```

## 📈 Output Format

The tool adds two new columns to your CSV:

- `phone_number`: Found phone number or "Not Available"
- `confidence`: High/Medium/Low/N/A

### Confidence Levels:
- **High**: Found on business directories (JustDial, IndiaMART)
- **Medium**: Found on company websites
- **Low**: Found in search results only
- **N/A**: No phone number found

## ⚙️ How It Works

1. **Query Generation**: Creates multiple search queries per company
   - "{company_name} phone number contact"
   - "{company_name} contact details"
   - "{director_name} chartered accountant phone"
   - "{cin} company contact details"

2. **Multi-source Search**:
   - Google search results
   - Company websites (top 3 results)
   - Business directories (JustDial, IndiaMART)

3. **Phone Extraction**:
   - Indian phone number patterns (+91XXXXXXXXXX, 10-digit)
   - Validation and deduplication
   - Confidence scoring based on source

4. **Rate Limiting**:
   - 2-5 second delays between requests
   - Respects website policies
   - Handles rate limits gracefully

## 🔒 Legal & Ethical Considerations

- **Public Data Only**: Scrapes only publicly available information
- **Rate Limited**: Includes delays to respect website policies
- **No Private Data**: Does not access private or restricted information
- **Compliance**: Users responsible for compliance with local laws

## 🚨 Limitations

- **Processing Speed**: ~30-60 seconds per company
- **Success Rate**: Varies (typically 30-70% depending on company visibility)
- **Rate Limits**: May encounter temporary blocks from search engines
- **Data Quality**: Results depend on publicly available information

## 🛡️ Safety Features

- **Row Limit**: Maximum 50 companies per batch (configurable)
- **Error Handling**: Graceful failure handling
- **Timeout Protection**: Request timeouts to prevent hanging
- **Input Validation**: CSV format and column validation

## 🔧 Troubleshooting

### Common Issues:

1. **"No results found"**
   - Company name might be too generic
   - Try adding director name or CIN
   - Check spelling and formatting

2. **"Rate limited"**
   - Wait a few minutes and retry
   - Reduce batch size
   - Check internet connection

3. **"Import errors"**
   - Verify all dependencies installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **"CSV format errors"**
   - Ensure 'company_name' column exists
   - Check for special characters
   - Verify CSV encoding (UTF-8 recommended)

### Performance Tips:

- **Smaller Batches**: Process 10-20 companies at a time
- **Peak Hours**: Avoid peak internet hours for better success rates
- **Clean Data**: Remove duplicates and clean company names
- **Patience**: Allow sufficient time for processing

## 📝 Example Workflow

1. **Prepare CSV**: Create CSV with company names
2. **Run Tool**: Use Streamlit app or CLI
3. **Monitor Progress**: Watch real-time updates
4. **Review Results**: Check confidence levels
5. **Download**: Save processed CSV
6. **Validate**: Manually verify high-priority contacts

## 🤝 Contributing

This tool is designed for legitimate business use cases. Please ensure compliance with:
- Website terms of service
- Local data protection laws
- Ethical scraping practices

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Verify CSV format
3. Test with sample data
4. Check internet connectivity

---

**Disclaimer**: This tool is for educational and legitimate business purposes only. Users are responsible for compliance with applicable laws and website terms of service.
