# csvtoexcel

Convert CSV files to Excel format with formatting options.

## Usage

Use Python pandas to convert CSV to Excel:

```python
import pandas as pd
df = pd.read_csv('file.csv')
df.to_excel('file.xlsx', index=False)
```