import bcrypt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def register(request):
    data = request.data
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not (name and email and password):
        return Response({'error': 'name, email, password required'}, status=status.HTTP_400_BAD_REQUEST)

    # PostgreSQL is case-sensitive: store original but check case-insensitively
    email_lower = email.lower()
    if User.objects.filter(email__iexact=email_lower).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    # Hash password with bcrypt before storing
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User.objects.create(email=email, name=name, password=hashed.decode('utf-8'))
    return Response({'message': 'User registered', 'user_id': str(user.id)}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return Response({'error': 'email and password required'}, status=status.HTTP_400_BAD_REQUEST)

    # PostgreSQL case-sensitive check: find by lowercased email
    email_lower = email.lower()
    try:
        user = User.objects.get(email__iexact=email_lower)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Verify hashed password with bcrypt
    stored_hash = user.password.encode('utf-8') if isinstance(user.password, str) else user.password
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })
