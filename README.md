# System Design Interview Practice

A web application that allows you to practice mock System Design interviews using AI-powered chat interface. The system simulates a real-world interview experience where you can ask clarifying questions and receive responses from an AI interviewer.

## Features

- **Start Interview**: Begin a new interview session with custom or preset system design questions
- **Chat Interface**: Real-time chat with AI interviewer that responds as a real interviewer would
- **Image Upload**: Upload and share images (diagrams, sketches, etc.) during interviews for AI analysis
- **Interview Management**: View, continue, and end interview sessions
- **Preset Questions**: Choose from popular system design questions like "Design YouTube", "Build a URL shortener", etc.
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend
- **Django 4.2.23**: Python web framework
- **Django REST Framework**: API framework
- **OpenAI API**: Integration with ChatGPT for AI responses
- **Pillow**: Image processing library
- **SQLite**: Database (can be easily changed to PostgreSQL/MySQL)

### Frontend
- **React 18**: JavaScript library for building user interfaces
- **CSS3**: Modern styling with responsive design
- **Axios**: HTTP client for API calls

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key
- Make (for using the Makefile commands)

### Quick Start (Recommended)

#### Option 1: Using the Run Script (Easiest)
```bash
# Install dependencies and start the application
./run.sh install
./run.sh start
```

#### Option 2: Using Make
1. **Install all dependencies:**
   ```bash
   make install
   ```

2. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run database migrations:**
   ```bash
   make migrate
   ```

4. **Start both servers:**
   ```bash
   make start-all
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Manual Setup

#### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the Django development server:**
   ```bash
   python manage.py runserver
   ```
   The backend will be available at `http://localhost:8000`

#### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```
   The frontend will be available at `http://localhost:3000`

### Available Commands

#### Using the Run Script
```bash
./run.sh start          # Start both backend and frontend servers
./run.sh stop           # Stop all running servers
./run.sh backend        # Start only the backend server
./run.sh frontend       # Start only the frontend server
./run.sh install        # Install all dependencies
./run.sh migrate        # Run database migrations
```

#### Using Make
```bash
make help          # Show all available commands
make install       # Install all dependencies
make start-all     # Start both backend and frontend servers
make start-backend # Start only the backend server
make start-frontend # Start only the frontend server
make stop          # Stop all running servers
make migrate       # Run Django migrations
make clean         # Clean up temporary files
```

## API Endpoints

- `POST /api/interview/start/` - Start a new interview
- `GET /api/interview/list/` - List all interviews
- `GET /api/interview/{id}/` - Get interview details
- `POST /api/interview/{id}/send/` - Send a message in an interview
- `POST /api/interview/{id}/end/` - End an interview

## Usage

1. **Start the application** by running both backend and frontend servers
2. **Open your browser** and navigate to `http://localhost:3000`
3. **Click "Start New Interview"** to begin a practice session
4. **Choose a question** from the presets or enter your own
5. **Begin the interview** by asking clarifying questions about the system design problem
6. **Share images** by dragging and dropping or clicking the camera icon to upload diagrams, sketches, or screenshots
7. **Continue the conversation** as you would in a real interview
8. **End the interview** when you're finished

## System Design Interview Tips

- Start by asking clarifying questions about requirements
- Discuss scale (users, data, traffic)
- Talk about data models and relationships
- Consider consistency, availability, and partition tolerance trade-offs
- Discuss caching strategies
- Mention monitoring and observability
- Consider security and privacy aspects

## Project Structure

```
system-designs-practice/
├── backend/
│   ├── backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── interview/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InterviewList.js
│   │   │   ├── InterviewChat.js
│   │   │   ├── StartInterview.js
│   │   │   └── *.css
│   │   ├── App.js
│   │   └── App.css
│   └── package.json
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.
