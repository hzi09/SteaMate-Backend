#!/bin/bash
echo "🚀 협업 필터링 모델 학습을 시작합니다..."
docker exec -it steamate-web-1 python manage.py shell <<EOF
from pickmate.ml_utils import train_collaborative_filtering
train_collaborative_filtering()
EOF
echo "✅ 모델 학습이 완료되었습니다!"
