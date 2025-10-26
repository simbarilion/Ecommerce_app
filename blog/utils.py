def is_content_manager(user):
    """Проверяет, состоит ли пользователь в группе контент-менеджеров"""
    return user.is_superuser or user.groups.filter(name="content_manager").exists()
