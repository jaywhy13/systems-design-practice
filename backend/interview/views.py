import base64
import os

import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from openai import OpenAI
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    Article,
    ArticleChat,
    ArticleMessage,
    ImageUpload,
    Interview,
    InterviewArticle,
    Message,
)
from .serializers import (
    ArticleChatSerializer,
    ArticleMessageSerializer,
    CreateInterviewSerializer,
    InterviewSerializer,
    MessageSerializer,
    SendArticleMessageSerializer,
    SendMessageSerializer,
)

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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


def encode_image_to_base64(image_path):
    """Encode image to base64 for OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@api_view(["POST"])
def start_interview(request):
    """Start a new interview session"""
    serializer = CreateInterviewSerializer(data=request.data)
    if serializer.is_valid():
        interview = Interview.objects.create(
            question=serializer.validated_data.get("question", "Design a URL shortener")
        )

        # Create initial system message
        initial_message = Message.objects.create(
            interview=interview,
            role="assistant",
            content=f"Hello! I'm your System Design interviewer. Let's begin with today's question: {interview.question}. Please start by asking any clarifying questions you have about the requirements.",
        )

        return Response(
            InterviewSerializer(interview).data, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def send_message(request, interview_id):
    """Send a message in an interview and get AI response"""
    interview = get_object_or_404(Interview, id=interview_id, is_active=True)
    serializer = SendMessageSerializer(data=request.data)

    if serializer.is_valid():
        # Save user message
        user_message = Message.objects.create(
            interview=interview,
            role="user",
            content=serializer.validated_data.get("content", ""),
        )

        # Handle image uploads
        images = serializer.validated_data.get("images", [])
        for image in images:
            ImageUpload.objects.create(message=user_message, image=image)

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
                    message_content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        }
                    )
                except Exception as e:
                    print(f"Error processing image: {e}")

            conversation.append({"role": msg.role, "content": message_content})

        try:
            # Get AI response
            response = client.chat.completions.create(
                model="gpt-4o", messages=conversation, max_tokens=500, temperature=0.7
            )

            ai_response = response.choices[0].message.content

            # Save AI response
            ai_message = Message.objects.create(
                interview=interview, role="assistant", content=ai_response
            )

            return Response(
                {
                    "user_message": MessageSerializer(user_message).data,
                    "ai_response": MessageSerializer(ai_message).data,
                }
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def end_interview(request, interview_id):
    """End an interview session and generate article recommendations"""
    interview = get_object_or_404(Interview, id=interview_id)
    interview.is_active = False
    interview.save()

    return Response(
        {
            "message": "Interview ended successfully",
            "interview": InterviewSerializer(interview).data,
        }
    )


@api_view(["GET"])
def get_interview(request, interview_id):
    """Get interview details and messages"""
    interview = get_object_or_404(Interview, id=interview_id)
    return Response(InterviewSerializer(interview).data)


@api_view(["GET"])
def list_interviews(request):
    """List all interviews"""
    interviews = Interview.objects.all().order_by("-created_at")
    return Response(InterviewSerializer(interviews, many=True).data)


@api_view(["POST"])
def start_article_chat(request, interview_id, article_id):
    """Start a chat session for discussing an article"""
    interview = get_object_or_404(Interview, id=interview_id)
    article = get_object_or_404(Article, id=article_id)

    # Create or get existing chat
    chat, created = ArticleChat.objects.get_or_create(
        interview=interview, article=article, defaults={"is_active": True}
    )

    if created:
        # Create initial message
        initial_message = ArticleMessage.objects.create(
            chat=chat,
            role="assistant",
            content=f"Hello! I'm here to help you discuss the article '{article.title}'. What would you like to know about it?",
        )

    return Response(ArticleChatSerializer(chat).data)


@api_view(["POST"])
def send_article_message(request, chat_id):
    """Send a message in an article chat"""
    chat = get_object_or_404(ArticleChat, id=chat_id, is_active=True)
    serializer = SendArticleMessageSerializer(data=request.data)

    if serializer.is_valid():
        # Save user message
        user_message = ArticleMessage.objects.create(
            chat=chat, role="user", content=serializer.validated_data["content"]
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
                "content": f"You are a helpful assistant discussing the article: {chat.article.title}. Use the following context to answer questions: {article_context}",
            }
        ]

        for msg in messages:
            conversation.append({"role": msg.role, "content": msg.content})

        try:
            # Get AI response
            response = client.chat.completions.create(
                model="gpt-4", messages=conversation, max_tokens=500, temperature=0.7
            )

            ai_response = response.choices[0].message.content

            # Save AI response
            ai_message = ArticleMessage.objects.create(
                chat=chat, role="assistant", content=ai_response
            )

            return Response(
                {
                    "user_message": ArticleMessageSerializer(user_message).data,
                    "ai_response": ArticleMessageSerializer(ai_message).data,
                }
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_article_chat(request, chat_id):
    """Get article chat details and messages"""
    chat = get_object_or_404(ArticleChat, id=chat_id)
    return Response(ArticleChatSerializer(chat).data)
