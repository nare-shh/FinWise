# FinWise - Indian Tax Assistant

FinWise is a modern web application designed to assist users with Indian tax-related queries and calculations. The application combines a React-based frontend with a Python FastAPI backend to provide a seamless user experience.

## Features

- Interactive tax calculation and assistance
- Modern, responsive user interface
- Real-time chat interface for tax queries
- Secure API endpoints for tax-related operations

## Tech Stack

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- Axios for API calls
- React Hot Toast for notifications

### Backend
- FastAPI
- Python 3.x
- Groq for AI-powered responses
- Uvicorn server

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- npm or yarn package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FinWise
```

2. Install frontend dependencies:
```bash
npm install
```

3. Install backend dependencies:
```bash
cd FinWise
pip install -r requirements.txt
```

## Running the Application

1. Start the backend server:
```bash
cd FinWise
python run.py
```

2. In a separate terminal, start the frontend development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173` (frontend) and `http://localhost:8000` (backend).

## Development

- Frontend development server: `npm run dev`
- Build frontend: `npm run build`
- Lint frontend code: `npm run lint`
- Preview production build: `npm run preview`

## Project Structure

```
FinWise/
├── project/          # Frontend React application
├── api/             # Backend API endpoints
├── main.py          # Main FastAPI application
├── chatbot.py       # Chatbot implementation
└── requirements.txt # Python dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers. 
