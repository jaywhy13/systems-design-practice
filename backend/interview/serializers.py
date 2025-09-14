from rest_framework import serializers
from .models import Interview, Message, ImageUpload, Article, InterviewArticle, ArticleChat, ArticleMessage

class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['id', 'image', 'uploaded_at']

class MessageSerializer(serializers.ModelSerializer):
    images = ImageUploadSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'timestamp', 'images']

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'url', 'source', 'summary', 'key_highlights', 'created_at']

class InterviewArticleSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)
    
    class Meta:
        model = InterviewArticle
        fields = ['id', 'article', 'relevance_score', 'created_at']

class ArticleMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleMessage
        fields = ['id', 'role', 'content', 'timestamp']

class ArticleChatSerializer(serializers.ModelSerializer):
    messages = ArticleMessageSerializer(many=True, read_only=True)
    article = ArticleSerializer(read_only=True)
    
    class Meta:
        model = ArticleChat
        fields = ['id', 'article', 'messages', 'created_at', 'is_active']

class InterviewSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    recommended_articles = InterviewArticleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Interview
        fields = ['id', 'created_at', 'updated_at', 'is_active', 'question', 'messages', 'recommended_articles']

class CreateInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['question']

class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=10000, required=False, allow_blank=True)
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True
    )

class SendArticleMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=10000)
