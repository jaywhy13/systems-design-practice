from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from openai import OpenAI
import os
import base64
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from .models import (
    Interview, Message, ImageUpload, Article, InterviewArticle, 
    ArticleChat, ArticleMessage
)
from .serializers import (
    InterviewSerializer, CreateInterviewSerializer, SendMessageSerializer, 
    MessageSerializer, ArticleChatSerializer, SendArticleMessageSerializer,
    ArticleMessageSerializer
)

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# System prompt for the interviewer
SYSTEM_PROMPT = """You are an interviewer for a System Design loop. Your role is to simulate a real-world interview. Follow these instructions closely:
	1.	Introduction:
	•	Start by introducing yourself as the interviewer.
	•	Present a concise, ambiguous problem statement, e.g., "Design YouTube," "Build a URL shortener," or "Create a global code deployment system."
	2.	Interview Style:
	•	The candidate (user) will drive the conversation by asking clarifying questions.
	•	You should reply concisely, giving only the information specifically requested.
	•	Avoid over-explaining or volunteering details unless explicitly asked.
	3.	Active Interviewing:
	•	If the candidate overlooks a key area (e.g., scaling, data modeling, consistency trade-offs, APIs, caching, monitoring, etc.), you may jump in to ask about gaps in their design, just as a real interviewer would.
	•	Keep these interruptions natural and occasional.
	4.	Tone & Flow:
	•	Be professional but approachable.
	•	Keep the session structured, realistic, and time-aware.
	5.	Image Analysis:
	•	If the candidate shares images (diagrams, sketches, etc.), analyze them and provide feedback on their system design approach.
	•	Ask clarifying questions about the design elements shown in the images.

Goal: Simulate a realistic, back-and-forth system design interview where the candidate must drive the design, clarify assumptions, and think through trade-offs, while you keep them honest with follow-ups.

Do not volunteer feedback unless asked for it. If you see a gap in the design, ask about it. However, ask one question at a time.

When providing feedback and questions about the design, provide feedback that is specific. Only tackle ONE specific issue at a time. 
Don't overwhelm the interviewee with too many questions or feedback at once. Address one issue at a time. 

"""

# Article sources
ARTICLE_SOURCES = {
    'shopify': 'https://shopify.engineering/',
    'robinhood': 'https://newsroom.aboutrobinhood.com/category/engineering/',
    'pinterest': 'https://medium.com/pinterest-engineering'
}

def encode_image_to_base64(image_path):
    """Encode image to base64 for OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_article_recommendations(interview):
    """Generate article recommendations based on interview content"""
    # Get interview conversation
    messages = interview.messages.all()
    conversation_text = " ".join([msg.content for msg in messages])
    
    # Create prompt for article recommendations
    recommendation_prompt = f"""
    Based on this system design interview conversation, recommend 3-5 relevant articles from engineering blogs.
    
    Interview Question: {interview.question}
    Conversation: {conversation_text[:2000]}
    
    Please recommend articles that cover concepts discussed in this interview. For each article, provide:
    1. Title
    2. URL (from shopify.engineering, newsroom.aboutrobinhood.com/category/engineering/, or medium.com/pinterest-engineering)
    3. Brief summary (2-3 sentences)
    4. Key highlights (3-5 bullet points)
    
    Format as JSON:
    {{
        "articles": [
            {{
                "title": "Article Title",
                "url": "https://...",
                "source": "shopify|robinhood|pinterest",
                "summary": "Brief summary...",
                "key_highlights": ["Point 1", "Point 2", "Point 3"]
            }}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": recommendation_prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse the response and create article objects
        # For now, we'll create some sample articles
        sample_articles = [
            {
                "title": "Building Scalable Systems at Shopify",
                "url": "https://shopify.engineering/building-scalable-systems",
                "source": "shopify",
                "summary": "Learn how Shopify engineers design and implement scalable systems that handle millions of requests daily.",
                "key_highlights": [
                    "Microservices architecture patterns",
                    "Database sharding strategies", 
                    "Caching implementation",
                    "Load balancing techniques",
                    "Monitoring and observability"
                ]
            },
            {
                "title": "Robinhood's Real-Time Trading Infrastructure",
                "url": "https://newsroom.aboutrobinhood.com/engineering/real-time-trading",
                "source": "robinhood", 
                "summary": "Explore how Robinhood built a real-time trading platform that processes millions of orders with low latency.",
                "key_highlights": [
                    "Real-time data processing",
                    "Low-latency architecture",
                    "Order matching algorithms",
                    "High availability design",
                    "Security considerations"
                ]
            },
            {
                "title": "Pinterest's Recommendation Engine",
                "url": "https://medium.com/pinterest-engineering/recommendation-engine",
                "source": "pinterest",
                "summary": "Discover how Pinterest's recommendation system personalizes content for millions of users.",
                "key_highlights": [
                    "Machine learning algorithms",
                    "Personalization strategies",
                    "A/B testing frameworks",
                    "Data pipeline architecture",
                    "Performance optimization"
                ]
            }
        ]
        
        # Create article objects and link them to the interview
        for article_data in sample_articles:
            article, created = Article.objects.get_or_create(
                url=article_data['url'],
                defaults={
                    'title': article_data['title'],
                    'source': article_data['source'],
                    'summary': article_data['summary'],
                    'key_highlights': article_data['key_highlights']
                }
            )
            
            # Link article to interview
            InterviewArticle.objects.get_or_create(
                interview=interview,
                article=article,
                defaults={'relevance_score': 0.8}
            )
            
    except Exception as e:
        print(f"Error generating article recommendations: {e}")

@api_view(['POST'])
def start_interview(request):
    """Start a new interview session"""
    serializer = CreateInterviewSerializer(data=request.data)
    if serializer.is_valid():
        interview = Interview.objects.create(
            question=serializer.validated_data.get('question', 'Design a URL shortener')
        )
        
        # Create initial system message
        initial_message = Message.objects.create(
            interview=interview,
            role='assistant',
            content=f"Hello! I'm your System Design interviewer. Let's begin with today's question: {interview.question}. Please start by asking any clarifying questions you have about the requirements."
        )
        
        return Response(InterviewSerializer(interview).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def send_message(request, interview_id):
    """Send a message in an interview and get AI response"""
    interview = get_object_or_404(Interview, id=interview_id, is_active=True)
    serializer = SendMessageSerializer(data=request.data)
    
    if serializer.is_valid():
        # Save user message
        user_message = Message.objects.create(
            interview=interview,
            role='user',
            content=serializer.validated_data.get('content', '')
        )
        
        # Handle image uploads
        images = serializer.validated_data.get('images', [])
        for image in images:
            ImageUpload.objects.create(
                message=user_message,
                image=image
            )
        
        # Get conversation history
        messages = interview.messages.all()
        conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for msg in messages:
            message_content = [{"type": "text", "text": msg.content}]
            
            # Add images to the message if any
            for img in msg.images.all():
                try:
                    image_path = img.image.path
                    base64_image = encode_image_to_base64(image_path)
                    message_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
                except Exception as e:
                    print(f"Error processing image: {e}")
            
            conversation.append({
                "role": msg.role,
                "content": message_content
            })
        
        try:
            # Get AI response
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Save AI response
            ai_message = Message.objects.create(
                interview=interview,
                role='assistant',
                content=ai_response
            )
            
            return Response({
                'user_message': MessageSerializer(user_message).data,
                'ai_response': MessageSerializer(ai_message).data
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def end_interview(request, interview_id):
    """End an interview session and generate article recommendations"""
    interview = get_object_or_404(Interview, id=interview_id)
    interview.is_active = False
    interview.save()
    
    # Generate article recommendations
    generate_article_recommendations(interview)
    
    return Response({
        'message': 'Interview ended successfully',
        'interview': InterviewSerializer(interview).data
    })

@api_view(['GET'])
def get_interview(request, interview_id):
    """Get interview details and messages"""
    interview = get_object_or_404(Interview, id=interview_id)
    return Response(InterviewSerializer(interview).data)

@api_view(['GET'])
def list_interviews(request):
    """List all interviews"""
    interviews = Interview.objects.all().order_by('-created_at')
    return Response(InterviewSerializer(interviews, many=True).data)

@api_view(['POST'])
def start_article_chat(request, interview_id, article_id):
    """Start a chat session for discussing an article"""
    interview = get_object_or_404(Interview, id=interview_id)
    article = get_object_or_404(Article, id=article_id)
    
    # Create or get existing chat
    chat, created = ArticleChat.objects.get_or_create(
        interview=interview,
        article=article,
        defaults={'is_active': True}
    )
    
    if created:
        # Create initial message
        initial_message = ArticleMessage.objects.create(
            chat=chat,
            role='assistant',
            content=f"Hello! I'm here to help you discuss the article '{article.title}'. What would you like to know about it?"
        )
    
    return Response(ArticleChatSerializer(chat).data)

@api_view(['POST'])
def send_article_message(request, chat_id):
    """Send a message in an article chat"""
    chat = get_object_or_404(ArticleChat, id=chat_id, is_active=True)
    serializer = SendArticleMessageSerializer(data=request.data)
    
    if serializer.is_valid():
        # Save user message
        user_message = ArticleMessage.objects.create(
            chat=chat,
            role='user',
            content=serializer.validated_data['content']
        )
        
        # Create context for AI response
        article_context = f"""
        Article: {chat.article.title}
        Summary: {chat.article.summary}
        Key Highlights: {', '.join(chat.article.key_highlights)}
        URL: {chat.article.url}
        """
        
        # Get conversation history
        messages = chat.messages.all()
        conversation = [
            {
                "role": "system", 
                "content": f"You are a helpful assistant discussing the article: {chat.article.title}. Use the following context to answer questions: {article_context}"
            }
        ]
        
        for msg in messages:
            conversation.append({
                "role": msg.role,
                "content": msg.content
            })
        
        try:
            # Get AI response
            response = client.chat.completions.create(
                model="gpt-4",
                messages=conversation,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Save AI response
            ai_message = ArticleMessage.objects.create(
                chat=chat,
                role='assistant',
                content=ai_response
            )
            
            return Response({
                'user_message': ArticleMessageSerializer(user_message).data,
                'ai_response': ArticleMessageSerializer(ai_message).data
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_article_chat(request, chat_id):
    """Get article chat details and messages"""
    chat = get_object_or_404(ArticleChat, id=chat_id)
    return Response(ArticleChatSerializer(chat).data)
