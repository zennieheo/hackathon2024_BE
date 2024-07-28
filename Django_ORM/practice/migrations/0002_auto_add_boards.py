# practice/migrations/0002_auto_add_boards.py
from django.db import migrations

def create_boards(apps, schema_editor):
    Board = apps.get_model('practice', 'Board')
    Board.objects.create(name='a게시판', description='Description for a게시판')
    Board.objects.create(name='b게시판', description='Description for b게시판')

class Migration(migrations.Migration):

    dependencies = [
        ('practice', '0001_initial'),  # 기존 초기 마이그레이션 파일 이름에 맞춰서 수정
    ]

    operations = [
        migrations.RunPython(create_boards),
    ]
