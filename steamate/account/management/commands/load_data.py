import os
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from account.models import Game, Genre
from dotenv import load_dotenv

load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

class Command(BaseCommand):
    """
    python manage.py load_data 명령어로 csv 파일에 정제된 데이터를 데이터베이스에 저장
    """
    help = "Load game data from a CSV file into the database"

    def handle(self, *args, **kwargs):
        '''
        CSV 파일에서 게임 데이터를 읽어와 데이터베이스에 저장
        '''
        file_path = os.path.join("account", "data", "steam_game_details.csv")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        # pandas로 CSV 데이터 로드 및 NaN 처리
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig").fillna({
                "release_date": "",
                "description": "",
                "review_score": 0
            })
        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {file_path}")
            df = pd.DataFrame()  # 빈 데이터프레임 반환
        except pd.errors.EmptyDataError:
            print(f"파일이 비어 있습니다: {file_path}")
            df = pd.DataFrame()  # 빈 데이터프레임 반환
        except pd.errors.ParserError as e:
            print(f"CSV 파일 파싱 오류 발생: {e}")
            df = pd.DataFrame()  # 빈 데이터프레임 반환
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
            df = pd.DataFrame()  # 빈 데이터프레임 반환
            

        game_count = 0
        genre_count = 0  # 장르 개수 추적

        for _, row in df.iterrows():
            try:
                # 필수 값 처리
                appid = int(row["appid"])
                title = row["name"].strip() if row["name"] else "Unknown"
                genre_names = row["genres"].split(",") if row["genres"] else []
                released_at = row["release_date"] if row["release_date"] else None
                description = row["detailed_description"] if row["detailed_description"] else ""
                review_score = float(row["positive_ratings"]) if row["positive_ratings"] else 0

                # 날짜 변환 (모델의 필드 타입에 맞게 변환)
                try:
                    released_at = datetime.strptime(released_at, "%d %b, %Y").date()
                except (ValueError, TypeError):
                    released_at = None

                # 게임 저장 (중복 체크 + 신규 생성 가능)
                game, created = Game.objects.get_or_create(
                    appid=appid,
                    defaults={
                        "title": title,
                        "released_at": released_at,
                        "description": description,
                        "review_score": review_score,
                    }
                )

                # 장르 추가 (새로운 장르가 생성된 경우만 카운트)
                for genre_name in genre_names:
                    genre, created_genre = Genre.objects.get_or_create(genre_name=genre_name.strip())
                    if created_genre:
                        genre_count += 1  # 새롭게 생성된 장르만 카운트

                game_count += 1

            except IntegrityError:
                self.stdout.write(self.style.WARNING(f"Duplicate entry skipped for appid {appid}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing row {row.to_dict()} -> {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully added {game_count} new games!")) # 추가된 게임 개수 출력
        self.stdout.write(self.style.SUCCESS(f"Successfully added {genre_count} new genres!"))  # 정확한 장르 개수 출력
