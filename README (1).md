# AI Blog Generator

A Django-based platform that uses a multi-agent AI pipeline to generate personalized blog content from a simple topic prompt. Content is generated using Google's Gemini API, automatically checked for plagiarism against existing posts, and personalized based on each user's writing history. Deployed end-to-end on Render with a managed PostgreSQL database.

## Features

- **Agentic Content Generation** – A controller agent orchestrates a multi-step pipeline: personalization → writing → plagiarism check → decision (rewrite if needed)
- **Personalization Engine** – Analyzes a user's past blogs to detect their preferred language and recurring topic interests, then subtly steers new content toward those themes
- **Plagiarism Detection** – Compares newly generated content against all existing posts (Jaccard similarity on tokenized text) and automatically triggers a rewrite if similarity exceeds 30%
- **Multi-Model Fallback** – Tries multiple Gemini models in order (`gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-3-flash-preview`), and falls back to a local template generator if all API calls fail, so the app stays demoable even offline
- **User Accounts** – Custom signup/login/logout flow using Django's built-in auth
- **Reviews & Ratings** – Readers can comment on and star-rate generated blogs
- **Analytics Dashboard** – Tracks total blogs generated, average generation time, average plagiarism score, and average rating
- **Multi-language Support** – Blogs can be generated in any language specified by the user
- **Cloud Deployment** – Live on Render with PostgreSQL in production and SQLite for local development

## Tech Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Backend        | Django 5.2                          |
| AI Generation  | Google Gemini API (`google-genai`)  |
| Database       | PostgreSQL (prod) / SQLite (local)  |
| Deployment     | Render, Gunicorn, WhiteNoise        |
| Language       | Python                              |

## Architecture: The Agentic Flow

Each blog request runs through a chain of agents (`blog/agents/`):

1. **Personalization Agent** – Looks at the user's last 20 blogs to detect their preferred language and top recurring topic keywords
2. **Writer Agent** – Sends the topic, language, and personalization context to Gemini to generate the article
3. **Plagiarism Agent** – Tokenizes the new content and compares it against every existing blog's content using set-based similarity
4. **Decision Agent** – If similarity exceeds the 30% threshold, the content is sent back to the Writer Agent for a rewrite; otherwise it's accepted as-is

All steps are logged and saved per-blog (`agent_log`) for transparency into how each post was produced.

## Project Structure

```
ai_blog_system/
├── accounts/               # Custom signup/login/logout
├── blog/
│   ├── agents/
│   │   ├── controller_agent.py       # Orchestrates the agentic pipeline
│   │   └── personalization_agent.py  # Builds user interest/language profile
│   ├── services/
│   │   └── gemini_service.py         # Gemini API calls + model fallback + offline fallback
│   ├── utils/
│   │   └── plagiarism.py             # Similarity scoring against past posts
│   ├── models.py           # Blog, Review, Rating models
│   └── views.py            # Home, dashboard, blog detail views
├── ai_blog_system/
│   └── settings.py         # Env-based config for local + Render deployment
├── requirements.txt
└── Procfile                 # Render deployment (migrate + gunicorn)
```

## Getting Started

### Prerequisites
- Python 3.10+
- A Google Gemini API key
- PostgreSQL (optional — SQLite is used automatically if not configured)

### Installation

```bash
# Clone the repository
git clone https://github.com/bhargavins91-pixel/ai-blog-generator.git
cd ai-blog-generator

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file in the project root with:
#   GEMINI_API_KEY=your_gemini_api_key
#   DJANGO_SECRET_KEY=your_secret_key
#   DJANGO_DEBUG=True
#   DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
#   DATABASE_URL=postgres://...   (optional — omit to use local SQLite)

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/accounts/signup/` to create an account, then log in to start generating blogs.

## Routes

| Path                     | Description                          |
|--------------------------|----------------------------------------|
| `/accounts/signup/`      | Create a new account                 |
| `/accounts/login/`       | Log in                               |
| `/accounts/logout/`      | Log out                              |
| `/`                      | Home — generate a blog, view all posts (sortable by newest/oldest) |
| `/blog/<id>/`            | View a blog, leave a review/rating   |
| `/dashboard/`            | Analytics — total blogs, avg. generation time, avg. plagiarism score, avg. rating |

## Deployment

Deployed on **Render** using Gunicorn and WhiteNoise for static file serving, with migrations run automatically on release via the Procfile. PostgreSQL connection is auto-configured from Render's `DATABASE_URL` environment variable using `dj-database-url`; falls back to local SQLite when unset.

Live demo: `<add your Render deployment link here>`

## Future Enhancements

- Expand personalization to consider reader engagement (ratings/reviews), not just the author's own history
- Add richer plagiarism detection beyond token-overlap similarity
- Support additional AI providers as fallback options
- CI/CD pipeline for automated testing and deployment

## License

This project is for academic and portfolio purposes.
