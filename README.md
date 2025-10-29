# EmiMeter: Logistics Emissions Calculator

A Streamlit dashboard for monitoring, calculating, and optimizing organizational carbon emissions. Input logistics and energy data to visualize CO₂ impact across categories, compare baseline and optimized scenarios, and drive measurable sustainability improvements.

## Features

- Real-time emissions calculations
- Interactive data input for multiple categories:
  - Transportation (Cars, Trucks, Buses, Planes)
  - Equipment (Forklifts)
  - Facilities (Lighting, Heating, Cooling, Computing)
  - Subcontractors
- Optimization scenarios with adjustable parameters:
  - EV Share for vehicle fleet
  - Kilometer reduction targets
  - Plane load factor optimization
- Visual analytics:
  - Category-wise emission share (Pie Chart)
  - Baseline vs Optimized comparison (Bar Chart)
- Sample data loading and reset functionality

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gdp-dashboard.git
cd gdp-dashboard
```

2. Install dependencies:
```bash
pip install streamlit pandas plotly
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

## Usage

1. Launch the application using the command above
2. Use the "Load Sample Data" button to populate with example values
3. Input your organization's activity data in the left panel
4. Adjust optimization parameters using the sliders
5. View real-time updates in the visualization panels
6. Use "Reset" to clear all inputs

## Technical Details

- Built with Streamlit, Pandas, and Plotly
- Emissions calculated in tons CO₂e using standard conversion factors
- Supports both baseline and optimized scenario modeling
- Responsive design with dark mode support

## License

This project is licensed under the MIT License - see the LICENSE file for details.
