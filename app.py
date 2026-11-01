from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import average_precision_score,f1_score,accuracy_score
R=Path(__file__).parent;D=R/'data'
st.set_page_config(page_title='초원 식물의 공간 점유 변화',layout='wide')
@st.cache_data
def data(name):return pd.read_parquet(D/name)
d=data('grid_analysis.parquet');maps=data('grid_maps.parquet')
st.title('초원 식물의 공간 점유 변화와 종 교체')
page=st.sidebar.radio('화면',['1. 연구 개요와 데이터','2. 식물 점유 소실의 조건','3. 소실 이후 공간 변화','4. 신규 점유 예측','5. 결론 및 검증'])
sp=st.sidebar.selectbox('식물종',sorted(d.species.unique()),index=sorted(d.species.unique()).index('Bouteloua gracilis'))
treat=st.sidebar.multiselect('방목 처리',sorted(d.treatment.unique()),default=sorted(d.treatment.unique()))
qs=st.sidebar.multiselect('조사구',sorted(d.quadrat.unique()),default=sorted(d.quadrat.unique()))
exclude=st.sidebar.checkbox('원자료가 종 오분류를 경고한 조사구 제외',value=False)
if exclude:qs=[q for q in qs if q not in ['gzgz_24','gzun_24','ungz_24']]
st.sidebar.caption('설명서에 명시된 고유 조사구 3곳. 설명서에는 gzun_24가 중복 기재되어 있어 다른 조사구로 임의 교정하지 않았습니다.')
years=st.sidebar.slider('시작 연도 범위',1997,2009,(1997,2009))
size=st.sidebar.selectbox('격자 한 변 (cm)',[10,5,20]);threshold=st.sidebar.selectbox('점유 기준',[0.,.01],format_func=lambda x:'양의 교차 면적' if x==0 else '격자 면적의 1% 이상')
base=d[d.quadrat.isin(qs)&d.treatment.isin(treat)&d.year.between(*years)&(d.size_cm==size)&(d.threshold==threshold)]
z=base[base.species==sp].copy()
st.caption('대상은 다각형으로 기록된 종입니다. 기록 없음은 생물학적 부재·맨땅·개체 사망과 같지 않습니다.')
def chart(fig):st.plotly_chart(fig,width='stretch')
def counts(f):st.caption(f'점유 격자·연도 행 {len(f):,}개 / 조사구 {f.quadrat.nunique()}개 / 목장 {f.pasture.nunique()}개 / 시작 연도 {f.year.nunique()}개. 격자 행은 독립 표본이 아닙니다.')
def summary(f,keys):
 a=f.groupby(keys,observed=True).agg(n=('lost','size'),losses=('lost','sum')).reset_index();a['소실률 (%)']=a.losses/a.n*100;return a
def insufficient(f):
 if f.empty:st.info('선택 조건의 유효 관측이 없습니다. 조사구·연도·방목 조건을 조정하세요.');return True
 if len(f)<10:st.info(f'유효 표본이 {len(f)}행으로 적어 비교 그래프를 생략합니다. 조건을 넓혀 주세요.');return True
 return False
if page.startswith('1.'):
 st.subheader('세 가지 연구 질문')
 st.write('① 점유 격자의 소실은 주변 식생과 방목 조건에 따라 어떻게 다른가? ② A만 있던 격자에서 A가 사라지면 무엇이 기록되는가? ③ 주변 종별 점유 정보를 추가하면 타종 신규 관측을 더 잘 예측하는가?')
 st.write('1997–2010년 콜로라도 6개 목장, 24개 1m² 고정 조사구. 관측 324 조사구·연도와 연속 관측 288쌍을 사용합니다. 2000년 12개 조사구 누락을 0으로 대체하지 않았습니다.')
 counts(z)
 st.write('같은 종의 다각형 합집합 → 도형 유효성 수정 → 고정 경계 자르기 → 격자 교차 면적 → 점유 여부. 원래 도형 면적 분석은 보조 근거로 유지합니다.')
 st.warning('속 수준·혼합·Crown·미상 기록을 특정 종으로 배정하지 않습니다. 일부 작은 사각형은 원자료에서 점을 0.25cm²로 변환한 기록입니다. 좌표 자동 정렬은 수행하지 않았습니다.')
 st.markdown('[원자료·설명서](https://esapubs.org/archive/ecol/E094/128/metadata.php) · [공식 보관본](https://doi.org/10.6084/m9.figshare.3556779.v1)')
elif page.startswith('2.'):
 if not insufficient(z):
  counts(z);z['주변 구간']=pd.cut(z.neighbor_other,[-1e-9,.1,.5,1.00001],labels=['0–10%','10–50%','50–100%'])
  a=summary(z,['주변 구간']);chart(px.bar(a,x='주변 구간',y='소실률 (%)',text='n',title='이전 해 주변 타종 점유율 구간별 A 격자 소실률',range_y=[0,100]))
  st.caption('막대 숫자 n은 이전 A 점유 격자·연도 수입니다. 주변 값은 선택한 격자의 인접 8칸 중 타종이 기록된 칸의 비율이며, 경계에서는 관측 가능한 3~5칸만 분모에 포함합니다.');st.dataframe(a,hide_index=True)
  q=summary(z,['quadrat','year','주변 구간']);chart(px.box(q,x='주변 구간',y='소실률 (%)',points='all',hover_data=['quadrat','year','n'],range_y=[0,100],title='조사구·연도별 소실률의 분포'))
  s=z.groupby(['quadrat','year']).agg(n=('lost','size'),loss=('lost','mean'),neighbor=('neighbor_other','mean')).reset_index();chart(px.scatter(s,x='neighbor',y='loss',size='n',hover_data=['quadrat','year'],labels={'neighbor':'주변 타종 점유율 평균','loss':'격자 소실 비율'},range_y=[0,1],title='조사구·연도 단위 주변 식생과 소실'))
  st.caption('점 하나는 조사구·연도입니다. 초기 피복, 식별 상태, 환경 차이의 영향을 분리한 인과효과가 아닙니다.')
  # Match years on observation availability, not focal-species presence.
  available=d[['quadrat','pasture','treatment','year']].drop_duplicates();available=available[available.quadrat.isin(qs)&available.year.between(*years)]
  eligible=available.groupby(['pasture','year']).treatment.nunique();eligible=set(eligible[eligible==4].index)
  b=z[[ (r.pasture,r.year) in eligible for r in z.itertuples() ]]
  if b.empty:st.info('현재 선택에서 네 방목 처리군의 공통 연도쌍이 없어 목장 내 비교를 표시하지 않습니다.')
  else:
   a=summary(b,['pasture','treatment']);chart(px.line(a,x='treatment',y='소실률 (%)',color='pasture',markers=True,hover_data=['n'],range_y=[0,100],title='목장 내 공통 연도쌍의 방목 처리별 소실률'));st.dataframe(a,hide_index=True)
  st.caption('unun 계속 비방목 / ungz 방목 시작 / gzun 방목 중단 / gzgz 계속 방목. 연결선은 같은 목장을 연결하며 시간 흐름을 뜻하지 않습니다. 목장별 반대 방향도 그대로 표시합니다.')
elif page.startswith('3.'):
 if not insufficient(z):
  a=z[z.a_only&(z.lost==1)];counts(a)
  st.write('분모: 이전 해 A만 점유하고 식별 불확실 기록이 없으며, 다음 해 A가 없는 격자. 다음 해 불확실 기록은 별도 범주입니다.')
  if not insufficient(a):
   s=a.groupby(['quadrat','state']).size().rename('n').reset_index();s['비율 (%)']=s.n/s.groupby('quadrat').n.transform('sum')*100
   chart(px.bar(s,x='quadrat',y='비율 (%)',color='state',hover_data=['n'],range_y=[0,100],title='A 단독 점유 소실 뒤 다음 관측의 기록 상태'));st.dataframe(s,hide_index=True)
   st.caption('이 표본에서는 이전 해 확인된 타종이 없으므로 다음 해 타종 기록은 신규 관측입니다. 실제 정착 시점이나 장기 공백 지속을 입증하지 않습니다.')
  allsp=base[base.a_only&(base.lost==1)];s=allsp.groupby(['species','state']).size().rename('n').reset_index()
  if len(s):
   s=s[s.groupby('species').n.transform('sum')>=10]
   s['비율 (%)']=s.n/s.groupby('species').n.transform('sum')*100;chart(px.bar(s,x='species',y='비율 (%)',color='state',hover_data=['n'],range_y=[0,100],title='같은 조사구·연도 조건에서 모든 종의 소실 후 상태 비교'))
  q=st.selectbox('지도 조사구',sorted(z.quadrat.unique()));y=st.selectbox('지도 시작 연도',sorted(z[z.quadrat==q].year.unique()))
  cols=st.columns(2);n=100//size
  for col,yr in zip(cols,[y,y+1]):
   m=maps[(maps.quadrat==q)&(maps.year==yr)&(maps.species==sp)&(maps.size_cm==size)];v=np.zeros(n*n);v[m.cell.to_numpy(dtype=int)]=m.cover
   fig=go.Figure(go.Heatmap(z=v.reshape(n,n),zmin=0,zmax=1,colorscale='Blues',colorbar=dict(title='A 피복 비율')));fig.update_layout(title=f'{q} · {yr} · {sp}',xaxis=dict(title='격자 열',constrain='domain'),yaxis=dict(title='격자 행',scaleanchor='x'),height=480);col.plotly_chart(fig,width='stretch')
  st.caption('지도는 이진 상태 대신 격자의 A 피복 비율을 보존합니다. 양쪽 지도는 동일한 0–1 색 범위를 사용합니다.')
elif page.startswith('4.'):
 st.write('10cm·양의 교차 면적 기준의 고정 시간 분리 실험입니다. 격자 크기 선택은 이 모델을 다시 학습하지 않습니다. 종·조사구·방목·연도 선택은 미사용 평가 자료를 필터링합니다.')
 st.write('학습 1997–2004 / 판정 기준 선택 2005–2006 / 평가 2007–2009 시작 연도쌍. 두 모델은 같은 로지스틱 회귀·같은 표본을 사용합니다.')
 p=data('test_predictions.parquet');p=p[(p.species==sp)&p.quadrat.isin(qs)&p.treatment.isin(treat)&p.year.between(*years)]
 metrics=pd.read_csv(D/'model_metrics.csv');meta=json.loads((D/'model_validation.json').read_text(encoding='utf8'))
 st.caption('예측 대상: t년에 A만 기록된 격자에서 t+1년에 확인된 타종이 하나라도 기록되는지. 미래 A 소실로 표본을 고르지 않았습니다. t+1 식별 불확실 격자는 평가에서 제외합니다.')
 if len(p)<30 or p.target.nunique()<2:st.info(f'평가 표본 {len(p)}행, 양성 {int(p.target.sum())}행으로 성능 비교를 표시하기에 부족합니다.')
 else:
  rows=[]
  for r in metrics.itertuples():rows.append({'모델':r.model,'Accuracy':accuracy_score(p.target,p[r.model]>=r.threshold),'F1':f1_score(p.target,p[r.model]>=r.threshold,zero_division=0),'PR-AUC (AP)':average_precision_score(p.target,p[r.model])})
  frame=pd.DataFrame(rows);chart(px.bar(frame.melt(id_vars='모델'),x='variable',y='value',color='모델',barmode='group',range_y=[0,1],labels={'variable':'평가 지표','value':'점수'},title='선택한 미사용 연도 표본의 두 모델 성능'));st.dataframe(frame,hide_index=True);st.caption(f'평가 {len(p)}행 / 양성 {int(p.target.sum())}행 / 조사구 {p.quadrat.nunique()}개. PR-AUC는 Average Precision으로 계산합니다.')
 st.subheader('전체 평가 표본의 불확실성');st.dataframe(metrics,hide_index=True);st.json(meta)
 st.caption('목장 단위 재표집은 두 모델에 동일하게 적용했습니다. 목장이 6개뿐이고 같은 장소의 미래 관측 평가이므로 다른 지역 일반화나 인과효과를 입증하지 않습니다.')
else:
 st.markdown((R/'연구결과.md').read_text(encoding='utf8'))
 s=d[(d.species==sp)&d.quadrat.isin(qs)&d.treatment.isin(treat)&d.year.between(*years)];a=summary(s,['size_cm','threshold']);chart(px.line(a,x='size_cm',y='소실률 (%)',color='threshold',markers=True,range_y=[0,100],title='선택한 표본의 격자 크기·점유 기준 민감도'));st.dataframe(a,hide_index=True)
 st.caption('도형 면적 소실률과 격자 소실률은 분모가 다릅니다. 큰 격자 내부의 위치 변화는 격자 유지로 분류될 수 있습니다.')
