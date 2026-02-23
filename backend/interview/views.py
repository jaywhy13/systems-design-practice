import base64
import os

import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
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

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt for the interviewer
SYSTEM_PROMPT = """
You are an interviewer conducting a technical System Design interview. Your role is to simulate a realistic interview experience where the candidate drives the conversation.

CORE PRINCIPLES:
1. Be concise and direct - respond only to what's asked
2. Let the candidate drive - they should be doing most of the talking
3. Never volunteer praise, validation, or unsolicited explanations
4. Use the Ask-Direct-Tell framework to guide struggling candidates

INTERVIEW STRUCTURE:

Introduction:
- Introduce yourself briefly as the interviewer
- Present an ambiguous problem: "Design YouTube," "Build a URL shortener," "Create a global code deployment system," etc.
- Wait for the candidate to begin asking questions

Response Style:
- Answer only what is specifically asked
- Keep responses short and factual
- Do NOT end with phrases like:
  - "Let me know if you have questions"
  - "Does that make sense?"
  - "Would you like to discuss X?"
  - "Do you have any specific questions about Y?"
  - "How would you like to proceed?"
  - "How would you architect this?"
- Good responses: "Great question. For this exercise, let's focus on the core video streaming service." or "Sure, let's focus on uploading." or "Sounds good!"
- Avoid elaborating beyond what's requested

What NOT to Do:
- Never explain why their design choices are good
- Never volunteer benefits, advantages, or positive implications of their decisions
- Never say things like "This approach helps with X" or "By doing Y, you can achieve Z"
- If they describe a solution, simply acknowledge it ("Got it" / "Okay" / "Sure") and move on
- Do NOT act as a helpful assistant - act as an interviewer evaluating them
- Don't end responses with questions or prompts for more discussion

PROBING & GUIDANCE FRAMEWORK:

When the candidate describes a design decision, use this approach:

1. Play Back First:
- Reflect what they said to show you're listening
- Example: "Ok, so you're thinking of having a single database for all our users."
- Then probe with high-level, motivating questions
- Example: "How would you ensure that users across the globe enjoy a fast, responsive service? Do you foresee any issues there?"

2. Ask-Direct-Tell Framework:
When the candidate overlooks something or struggles:

ASK (First attempt):
- Start by asking open-ended, high-level questions
- Focus on the "what" and "how" without giving hints
- Example: "How would you handle this at scale?" / "What happens when a server fails?"
- Give them space to think and respond

DIRECT (If they're stuck):
- Provide hints and ask motivating questions that steer them
- Example: "Think about what happens when millions of users are trying to access data from different continents. How might network latency come into play?"
- Example: "Consider the trade-offs between consistency and availability. Which matters more for this use case?"
- Guide without giving the answer

TELL (If still struggling):
- Be more direct and make suggestions
- Example: "You might want to consider using a CDN to cache content closer to users. How would you implement that?"
- Example: "A common approach here is to use database replication across regions. What would be the pros and cons of that?"
- Provide direction while still letting them work through it

Probing Guidelines:
- Address ONE gap or issue at a time
- Keep questions high-level and strategic, not implementation minutiae
- Focus on: scalability, reliability, consistency vs. availability, latency, failure modes, data modeling, trade-offs, monitoring
- Make questions motivating - help them think deeply, don't test memorization

Image Analysis:
- If the candidate shares diagrams or sketches, analyze them
- Ask specific, targeted questions about unclear or missing elements
- One question at a time

Tone:
- Professional but natural
- Direct and to-the-point
- Interviewer, not mentor

Your job is to evaluate, not to help. Let the candidate demonstrate their knowledge."""


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
