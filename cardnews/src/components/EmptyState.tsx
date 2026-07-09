export function EmptyState({ loading }: { loading: boolean }) {
  return (
    <div
      style={{
        minHeight: '70vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 20,
        textAlign: 'center',
      }}
    >
      <div style={{ display: 'flex', gap: 10 }}>
        <div style={{ width: 44, height: 58, background: '#272729', borderRadius: 4 }} />
        <div style={{ width: 44, height: 58, background: '#f7e9d7', borderRadius: 4, outline: '1px solid #e0e0e0' }} />
        <div style={{ width: 44, height: 58, background: '#0066cc', borderRadius: 4 }} />
        <div style={{ width: 44, height: 58, background: '#ffd23e', borderRadius: 4 }} />
      </div>
      <div style={{ fontSize: 21, fontWeight: 600, letterSpacing: '-0.3px' }}>
        {loading ? '카드뉴스를 만들고 있습니다…' : '아직 생성된 카드가 없습니다'}
      </div>
      <div style={{ fontSize: 15, color: '#7a7a7a', lineHeight: 1.6, maxWidth: 380 }}>
        {loading
          ? '카피를 쓰고 카드에 배치하는 중입니다. 10~30초 정도 걸려요.'
          : '왼쪽에서 디자인 스킨과 주제 분야를 고르고 제목을 입력한 뒤 "카드뉴스 생성하기"를 눌러주세요.'}
      </div>
    </div>
  );
}
