from .models import Message

def unread_messages(request):
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return {'unread_messages_count': unread_count}
    return {'unread_messages_count': 0}