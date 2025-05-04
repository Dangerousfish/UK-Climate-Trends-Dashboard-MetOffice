# UK Climate Trends Dashboard

This repository contains scripts and data for analysing historical UK climate station data sourced from the Met Office. The Streamlit dashboard lets you explore temperature, rainfall, and sunshine trends interactively.

## Files

- **compile_climate_data.py**: Downloads, cleans, and combines station data into combined_uk_station_climate_data.csv.

- **station_coordinates.csv**: Extracted latitude/longitude for each station.

- **combined_uk_station_climate_data.csv**: Cleaned climate data ready for analysis.

- **main.py**: Streamlit app providing interactive dashboard.

- **.gitignore**: Files and patterns to ignore.

## Requirements

```
Python 3.8+
```

### Install dependencies:

```
pip install pandas requests plotly streamlit
```

## Usage

### Compile data:

```
python compile_climate_data.py
```

### Run the dashboard:

```
python -m streamlit run main.py
```

Open the URL shown in the terminal (e.g. http://localhost:8501) in your browser.

## Project Structure

```
Temperatures_uk/
├── compile_climate_data.py
├── main.py
├── station_coordinates.csv
├── combined_uk_station_climate_data.csv
├── .gitignore
└── README.md
```

## Contributing

Contributions welcome! Please open issues or pull requests.

## License

This project is licensed under the MIT License.
