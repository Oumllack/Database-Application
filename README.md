# Database Management System 

A comprehensive web application built with Streamlit for managing and tracking Ivorian students residing in Siberia. This system provides an efficient way to maintain student records, visualize data through interactive dashboards, and automatically synchronize with Google Sheets.

## Key Features

- 📊 Real-time data visualization with interactive charts and statistics
- 🔍 Advanced filtering and search capabilities
- 📱 Responsive and user-friendly interface
- 🔄 Automatic synchronization with Google Sheets
- 📈 Student management (add, edit, delete records)
- 🎯 Data analysis and reporting tools

## Tech Stack

- Frontend: Streamlit
- Backend: Python
- Database: MySQL
- Data Visualization: Plotly
- Cloud Integration: Google Sheets API

## Project Structure

```
Database-App/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .streamlit/
│   ├── config.toml       # Streamlit configuration
│   └── secrets.toml      # Environment variables (to be created)
├── README.md             # Project documentation
└── .gitignore           # Git ignore file
```

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/Oumllack/Database-App.git
cd Database-App
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Create `.streamlit/secrets.toml` with your database credentials:
```toml
[mysql]
host = "your-host"
user = "your-username"
password = "your-password"
database = "cirt_db"
```

4. Run the application:
```bash
streamlit run app.py
```

## Google Sheets Integration

1. Create a `sheet_id.txt` file containing your Google Sheets ID
2. Configure Google Sheets API credentials in `credentials.json`

## License

This project is licensed under the MIT License.

## Contact

For any questions or support, please open an issue in the repository. 
