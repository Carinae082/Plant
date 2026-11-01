# 초원 식물의 공간 점유 변화 — 계획서 기준 보완본

원본 계획서의 세 질문에 맞춘 웹앱입니다. 기존 분석은 상위 폴더에 보존하고, 이 폴더의 앱과 보고서를 최신 보완본으로 사용합니다.

## 실행
Python 3.13에서 다음을 실행합니다.

```powershell
cd "C:\Users\송형륜\Documents\Codex\2026-10-31\e\outputs\grassland-research\final\revision"
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

기존 앱이 8501 포트를 사용하면 마지막 명령에 `--server.port 8502`를 붙입니다.

## 구성
- app.py: 다섯 화면, 실제 표본 필터
- data: 격자별 자료, 모델 평가 확률, 분할과 설정, 집계표
- graphs: 연구 질문별 PNG
- 연구결과.md: 방법·결과·해석·제안
- validation.json: 기존 격자 분석과의 수치 대조
- 전체 프로젝트 ZIP의 scripts: 추가 분석과 검증 코드

추가 분석은 기존 `phase2/species_geometry.parquet`와 `phase2/spatial_transitions.csv`를 재사용합니다. 전체 프로젝트 폴더에서 `scripts/phase4_plan_grid.py`, `phase5_predict.py`, `phase6_deliver.py`, `validate_revision.py` 순서로 실행합니다. 기존 원자료 재현은 상위 README를 따릅니다. 앱 실행에는 사전 계산된 data만 필요합니다.

## 정의
기본10cm에서 양의 교차 면적을 점유로 정의합니다. 1% 기준과5·20cm는 민감도입니다. 단독 점유는 확인된 다각형 종 A만 기록되고 불확실 다각형이 없는 상태이며, 점 기록의 부재를 보장하지 않습니다. 소실은 A의 다음 해 다각형 기록이 없는 상태입니다.

예측은 t년에 A만 있던 전체 후보에서 t+1 타종 신규 관측을 예측합니다. 미래 A 소실로 후보를 선택하지 않습니다. 미래 식별 불확실 기록은 목표 판정에서 제외하며 이 선택이 일반화를 제한합니다. 같은 조사구의 미래 관측 성능이며 새로운 지역 성능이 아닙니다.

## 배포
저장소 https://github.com/Carinae082/Plant 는 지정되어 있으나, 마지막 파일 쓰기 시도는 연결 도구의 403 오류로 거부됐습니다. 공개 앱 URL은 아직 없습니다.

이 폴더의 내용물을 저장소 루트에 올린 뒤 Streamlit Community Cloud에서 저장소 `Carinae082/Plant`, 브랜치 `main`, 파일 `app.py`, Python3.13을 선택합니다. ZIP 자체를 올리면 앱이 실행되지 않습니다.

GitHub Settings → Applications → Installed GitHub Apps → 연결 앱 Configure에서 Plant 접근 대상을 확인할 수 있습니다. 사용자가 앱이 요청하지 않은 쓰기 권한을 임의로 추가할 수는 없습니다. 읽기 전용 연결이면 웹 직접 업로드나 쓰기 지원 연결을 사용해야 합니다. 계정 로그인과 권한 동의는 사용자가 수행합니다.

## 출처와 AI
Chu et al.(2013), https://doi.org/10.1890/13-0121.1 ; https://doi.org/10.6084/m9.figshare.3556779.v1 . Shortgrass Steppe LTER 제공 자료입니다.

OpenAI (2026). Codex(GPT-6 계열; 보완 작업의 정확한 모델 버전은 별도 확인하지 않음). 생성일2026-11-01. 입력 요청: 기존 결과를 원본 계획서의 격자 소실·단독 점유 이후 상태·주변 정보 추가 예측 비교에 맞추어 보완. 도구 안내 https://openai.com/codex/ . AI는 코드 작성·검증·초안 작성을 보조했습니다. 제출자는 분석 정의, 결과 해석, 적용 제안을 검토하고 데이터 로딩·사이드바·차트 코드를 설명해야 합니다. 학생 개인정보와 원본 학교 안내문은 배포 파일에 포함하지 않습니다.


## 최종 검수와 파일 선택
최신 분석은 final/revision에 있습니다. 상위 app.py와 final의 기존 보고서는 이전 단계 보존본입니다.
전체 ZIP을 풀고 프로젝트 루트에서 `python -m pip install -r final/revision/requirements.txt`를 실행한 뒤 위 분석 순서를 따릅니다.
최신 앱 실행: `python -m streamlit run final/revision/app.py --server.port 8502 --global.developmentMode false`.
배포용 ZIP은 내용물을 저장소 루트에 풀어 사용합니다. 보고서와 발표자료는 전체 ZIP에 포함됩니다.
웹앱 12개 화면·필터 조합과 기존 격자 집계 4,490행의 수치 일치를 확인했습니다. 새 가상환경에 의존성을 처음부터 설치하는 검사는 수행하지 않았습니다.
발표자료 6장 전체의 PNG 렌더링을 확인했습니다. 실제 PowerPoint 데스크톱에서 재렌더링한 검사는 아닙니다.
공개 GitHub 파일 업로드와 Streamlit 로그인·공개 URL 확인은 완료되지 않았습니다.
