import time
from django.core.management.base import BaseCommand
from account.models import Game, GameTag, Tag
from account.utils import get_steam_tags
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "태그가 없는 게임에 Steam에서 크롤링한 태그를 추가"
    
    def handle(self, *args, **options):
        games = Game.objects.all()
        updated_count = 0
        
        for game in games:
            if GameTag.objects.filter(game=game).exists():
                continue
            
            tags = get_steam_tags(game.appid)
            if not tags:
                logger.warning(f"게임 태그 크롤링 실패 (appid: {game.appid})")
                continue

            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                GameTag.objects.get_or_create(game=game, tag=tag)
            
            updated_count += 1
            time.sleep(0.5)
        
        self.stdout.write(self.style.SUCCESS(f"총 {updated_count}개의 게임에 태그를 추가했습니다."))