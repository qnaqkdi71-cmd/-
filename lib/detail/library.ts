import type {
  Faq,
  GenerateInput,
  Item,
  PageContent,
  Stat,
  Testimonial,
} from "./types";

/**
 * 직업별 맞춤 문구 프리셋.
 * 여기 없는 직업을 넣어도 generic 생성기가 직업 이름을 넣어 자연스러운 페이지를 만듭니다.
 */
interface Preset {
  label: string;
  /** 매칭용 키워드 (입력에 이 단어가 포함되면 이 프리셋 사용) */
  aliases: string[];
  /** 문의 행동을 부르는 단어. 예: "상담", "진료 상담" */
  consultWord?: string;
  heroSubtitle?: (label: string) => string;
  problems?: string[];
  services?: Item[];
  why?: Item[];
  faq?: Faq[];
  testimonials?: Testimonial[];
}

const PRESETS: Preset[] = [
  {
    label: "변호사",
    aliases: ["변호사", "법률", "로펌", "법무법인"],
    consultWord: "법률 상담",
    heroSubtitle: () =>
      "혼자 고민하다 시기를 놓치면 더 불리해집니다. 사건 초기부터 정확한 전략으로 대응해야 결과가 달라집니다. 지금 바로 무료 법률 상담을 받아보세요.",
    problems: [
      "상대방에게서 내용증명·소송이 들어와 막막하신가요?",
      "인터넷 검색만으로는 내 상황에 맞는 답을 찾기 어려우신가요?",
      "변호사 선임 비용이 부담돼 망설이고 계신가요?",
      "지금 대응이 늦어질수록 불리해질까 불안하신가요?",
    ],
    services: [
      { title: "사건 분석", desc: "사실관계와 증거를 꼼꼼히 검토해 승소 가능성과 리스크를 솔직하게 알려드립니다." },
      { title: "맞춤 전략 수립", desc: "형사·민사·가사 등 사건 유형에 맞춰 가장 유리한 대응 방향을 설계합니다." },
      { title: "서면·출석 대리", desc: "복잡한 서류 작성부터 조사·재판 출석까지 전 과정을 대리합니다." },
      { title: "합의·협상", desc: "무리한 소송보다 유리한 합의가 가능한지 먼저 검토해 시간과 비용을 아낍니다." },
    ],
    faq: [
      { q: "상담만 받아도 비용이 드나요?", a: "첫 상담은 무료로 진행합니다. 부담 없이 상황부터 말씀해 주세요." },
      { q: "이미 소송이 진행 중인데 지금 의뢰해도 되나요?", a: "네, 진행 단계와 상관없이 검토 가능합니다. 오히려 빠를수록 대응 폭이 넓어집니다." },
      { q: "비용은 어떻게 책정되나요?", a: "사건 난이도와 진행 범위에 따라 다르며, 착수 전에 명확하게 안내해 드립니다." },
      { q: "비밀은 지켜지나요?", a: "상담 내용은 변호사의 비밀유지 의무에 따라 철저히 보호됩니다." },
    ],
  },
  {
    label: "세무사",
    aliases: ["세무사", "세무", "기장", "절세", "세무회계"],
    consultWord: "세무 상담",
    heroSubtitle: () =>
      "세금은 아는 만큼 아낍니다. 놓치기 쉬운 공제와 절세 포인트까지 꼼꼼히 챙겨, 낼 세금은 줄이고 가산세 걱정은 없애드립니다.",
    problems: [
      "세금이 왜 이렇게 많이 나왔는지 이해가 안 되시나요?",
      "종합소득세·부가세 신고 때만 되면 막막하신가요?",
      "기장을 맡기고 싶은데 비용이 걱정되시나요?",
      "가산세·세무조사가 나올까 불안하신가요?",
    ],
    services: [
      { title: "기장 대행", desc: "매출·매입 정리부터 신고까지, 사장님은 사업에만 집중하실 수 있게 맡아드립니다." },
      { title: "절세 컨설팅", desc: "업종·규모에 맞는 공제·감면을 찾아 합법적으로 세금을 최대한 줄여드립니다." },
      { title: "종합소득세·부가세 신고", desc: "복잡한 신고를 정확하게 처리해 가산세 리스크를 없앱니다." },
      { title: "양도·상속·증여 상담", desc: "큰 세금이 걸린 거래는 미리 설계해야 아낄 수 있습니다." },
    ],
    faq: [
      { q: "기장 수수료는 얼마인가요?", a: "매출 규모와 업종에 따라 다르며, 상담 시 정확하게 안내해 드립니다." },
      { q: "지금 신고 기한이 얼마 안 남았는데 가능한가요?", a: "네, 급한 신고 건도 최대한 빠르게 처리해 드립니다. 바로 연락 주세요." },
      { q: "다른 세무사에서 옮겨와도 되나요?", a: "네, 자료 이관부터 도와드리니 번거로움 없이 옮기실 수 있습니다." },
      { q: "절세가 정말 되나요?", a: "합법적인 범위에서 놓친 공제·감면을 찾아드리며, 예상 절감액을 먼저 알려드립니다." },
    ],
  },
  {
    label: "노무사",
    aliases: ["노무사", "노무", "인사", "부당해고", "산재", "임금체불"],
    consultWord: "노무 상담",
    heroSubtitle: () =>
      "부당해고, 임금체불, 산재… 혼자 대응하기 어려운 문제, 노무사가 근로자·사업주 양쪽의 리스크를 정확히 짚어 해결해 드립니다.",
    problems: [
      "부당하게 해고당했는데 어떻게 대응할지 모르시겠나요?",
      "받아야 할 임금·퇴직금을 못 받고 계신가요?",
      "산재 처리가 복잡해 포기하고 계신가요?",
      "사업주로서 노동법 리스크가 걱정되시나요?",
    ],
    services: [
      { title: "부당해고 구제", desc: "노동위원회 구제신청부터 심문까지 대리해 복직·보상을 이끌어냅니다." },
      { title: "임금체불 대응", desc: "진정·소송 절차로 밀린 임금과 퇴직금을 받아냅니다." },
      { title: "산재 신청 대행", desc: "요양·휴업급여 등 받을 수 있는 보상을 빠짐없이 챙겨드립니다." },
      { title: "인사노무 자문", desc: "취업규칙·근로계약·4대보험까지 사업장 리스크를 사전에 정리합니다." },
    ],
  },
  {
    label: "손해사정사",
    aliases: ["손해사정", "보험금", "보험청구"],
    consultWord: "보상 상담",
    heroSubtitle: () =>
      "보험사가 주는 대로 받고 계신가요? 받아야 할 보험금, 손해사정사가 제대로 계산해 정당한 보상을 받아드립니다.",
    problems: [
      "보험금이 생각보다 적게 나와 억울하신가요?",
      "보험사에서 지급을 거절당하셨나요?",
      "어떤 서류를 준비해야 할지 막막하신가요?",
      "후유장해·진단 기준이 복잡해 포기하려 하시나요?",
    ],
    services: [
      { title: "보험금 재산정", desc: "약관과 진단 내용을 근거로 받아야 할 정당한 금액을 다시 계산합니다." },
      { title: "지급 거절 대응", desc: "부지급·삭감 사유를 반박해 지급을 이끌어냅니다." },
      { title: "서류·증빙 준비", desc: "필요한 진단서·자료를 정확히 갖춰 심사 통과율을 높입니다." },
      { title: "합의금 검토", desc: "보험사 제시액이 적정한지 검토해 손해 보지 않게 돕습니다." },
    ],
  },
  {
    label: "공인중개사",
    aliases: ["공인중개사", "부동산", "중개", "매매", "전세", "월세"],
    consultWord: "부동산 상담",
    heroSubtitle: () =>
      "내 집 마련도, 안전한 계약도 결국 사람이 중요합니다. 시세부터 권리관계까지 꼼꼼히 챙겨 손해 없는 거래를 도와드립니다.",
    problems: [
      "시세를 몰라 비싸게 사거나 싸게 팔까 걱정되시나요?",
      "전세사기·깡통전세가 불안하신가요?",
      "복잡한 계약서와 권리관계가 헷갈리시나요?",
      "매물이 안 나가 마음만 급하신가요?",
    ],
    services: [
      { title: "매물 분석·시세 진단", desc: "실거래가와 주변 시세를 근거로 적정 가격을 알려드립니다." },
      { title: "안전 계약 검토", desc: "등기부·권리관계를 확인해 사기·분쟁 위험을 사전에 차단합니다." },
      { title: "매도·매수 대행", desc: "매물 홍보부터 협상, 잔금까지 전 과정을 책임집니다." },
      { title: "임대 관리 상담", desc: "전월세 세팅과 임차인 관리까지 함께 고민해 드립니다." },
    ],
  },
  {
    label: "인테리어",
    aliases: ["인테리어", "리모델링", "시공", "도배", "셀프인테리어", "집수리"],
    consultWord: "견적 상담",
    heroSubtitle: () =>
      "예산은 지키고, 하자는 없게. 상담부터 시공, 사후관리까지 한 곳에서 책임지는 믿을 수 있는 인테리어를 약속합니다.",
    problems: [
      "견적이 업체마다 달라 뭘 믿어야 할지 모르시겠나요?",
      "시공 후 하자·추가금 폭탄이 걱정되시나요?",
      "원하는 느낌을 어떻게 설명해야 할지 막막하신가요?",
      "공사 기간 동안 소통이 안 될까 불안하신가요?",
    ],
    services: [
      { title: "무료 현장 실측·상담", desc: "직접 방문해 공간을 확인하고, 예산에 맞는 현실적인 방향을 제안합니다." },
      { title: "3D 디자인 제안", desc: "완성된 모습을 미리 확인하고 결정하실 수 있습니다." },
      { title: "투명한 견적", desc: "자재·인건비를 항목별로 공개해 추가금 없는 견적을 드립니다." },
      { title: "책임 시공·A/S", desc: "직접 관리하는 시공팀과 시공 후 하자보수까지 보장합니다." },
    ],
    faq: [
      { q: "견적 상담은 무료인가요?", a: "네, 현장 실측과 견적 상담까지 무료로 진행합니다." },
      { q: "공사 기간은 얼마나 걸리나요?", a: "평형과 범위에 따라 다르며, 상담 시 일정표로 명확히 안내해 드립니다." },
      { q: "하자가 생기면 어떻게 하나요?", a: "시공 후 A/S 기간을 보장하며, 연락 주시면 빠르게 조치합니다." },
      { q: "예산이 적어도 상담 가능한가요?", a: "네, 예산에 맞춰 우선순위를 정하는 것부터 함께 도와드립니다." },
    ],
  },
  {
    label: "건축사",
    aliases: ["건축사", "건축", "설계", "신축", "인허가", "감리"],
    consultWord: "설계 상담",
    heroSubtitle: () =>
      "좋은 건물은 좋은 설계에서 시작됩니다. 인허가부터 설계·감리까지, 예산과 법규를 모두 지키며 후회 없는 건축을 돕습니다.",
    problems: [
      "어디서부터 시작해야 할지 막막하신가요?",
      "인허가 절차가 복잡해 엄두가 안 나시나요?",
      "예산 초과·설계 변경이 걱정되시나요?",
      "시공사만 믿어도 될지 불안하신가요?",
    ],
    services: [
      { title: "기획·타당성 검토", desc: "땅의 조건과 법규를 분석해 지을 수 있는 최적안을 제안합니다." },
      { title: "인허가 대행", desc: "복잡한 건축 인허가 절차를 대신 처리해 드립니다." },
      { title: "설계", desc: "쓰임과 예산에 맞는 실용적이고 아름다운 설계를 진행합니다." },
      { title: "감리", desc: "설계대로 제대로 지어지는지 현장을 감독해 품질을 지킵니다." },
    ],
  },
  {
    label: "변리사",
    aliases: ["변리사", "특허", "상표", "디자인등록", "지식재산", "실용신안"],
    consultWord: "특허 상담",
    heroSubtitle: () =>
      "아이디어와 브랜드는 등록해야 지킬 수 있습니다. 특허·상표 출원부터 분쟁 대응까지, 권리를 확실하게 확보해 드립니다.",
    problems: [
      "내 아이디어를 뺏길까 걱정되시나요?",
      "상표를 먼저 등록당할까 불안하신가요?",
      "출원 절차가 복잡해 미루고 계신가요?",
      "경쟁사가 내 권리를 침해하고 있나요?",
    ],
    services: [
      { title: "선행조사", desc: "출원 전 유사 특허·상표를 조사해 등록 가능성을 먼저 확인합니다." },
      { title: "특허·상표 출원", desc: "권리 범위를 넓게 확보하도록 명세서·청구항을 전략적으로 작성합니다." },
      { title: "중간사건 대응", desc: "거절이유 통지에 논리적으로 대응해 등록률을 높입니다." },
      { title: "분쟁·침해 대응", desc: "침해 경고부터 심판·소송까지 권리를 지켜드립니다." },
    ],
  },
  {
    label: "한의원",
    aliases: ["한의사", "한의원", "한방", "침", "추나", "한약"],
    consultWord: "진료 상담",
    heroSubtitle: () =>
      "증상만 잠재우는 것이 아니라 원인을 찾습니다. 체질과 생활을 함께 살펴 몸이 스스로 회복하도록 돕는 맞춤 한방 치료.",
    problems: [
      "여러 곳을 다녀도 그때뿐이신가요?",
      "원인을 모른 채 증상만 반복되시나요?",
      "몸이 예전 같지 않아 걱정되시나요?",
      "나에게 맞는 치료가 무엇인지 궁금하신가요?",
    ],
    services: [
      { title: "체질·증상 진단", desc: "맥진과 문진으로 몸 상태와 원인을 꼼꼼히 살핍니다." },
      { title: "맞춤 한방 치료", desc: "침·추나·약침 등 증상에 맞는 치료를 조합합니다." },
      { title: "맞춤 한약", desc: "체질과 증상에 맞춰 조제한 한약으로 회복을 돕습니다." },
      { title: "생활 관리 지도", desc: "치료 효과가 오래가도록 식습관·자세까지 함께 관리합니다." },
    ],
  },
  {
    label: "심리상담",
    aliases: ["심리상담", "상담사", "심리", "마음", "우울", "불안", "부부상담"],
    consultWord: "심리 상담",
    heroSubtitle: () =>
      "힘든 마음, 혼자 견디지 않아도 됩니다. 판단하지 않고 안전하게 들어드리며, 지금보다 나아지는 길을 함께 찾습니다.",
    problems: [
      "이유 없이 우울하거나 불안하신가요?",
      "누구에게도 말하기 어려운 고민이 있으신가요?",
      "관계 때문에 지치고 힘드신가요?",
      "상담이 처음이라 망설여지시나요?",
    ],
    services: [
      { title: "개인 심리상담", desc: "우울·불안·번아웃 등 마음의 어려움을 안전하게 다룹니다." },
      { title: "관계·부부 상담", desc: "가족·연인·직장 관계의 갈등을 함께 풀어갑니다." },
      { title: "심리 검사", desc: "객관적인 검사로 나를 이해하는 것부터 시작합니다." },
      { title: "비밀 보장", desc: "모든 상담 내용은 철저히 비밀로 보호됩니다." },
    ],
  },
];

const GENERIC_TESTIMONIALS: Testimonial[] = [
  { name: "김○○ 님", text: "막막했는데 차근차근 설명해 주셔서 믿고 맡겼어요. 결과도 만족스럽습니다.", rating: 5 },
  { name: "이○○ 님", text: "상담부터 다르더라고요. 비용도 투명하게 알려주셔서 안심됐습니다.", rating: 5 },
  { name: "박○○ 님", text: "여러 곳을 알아봤는데 여기가 가장 친절하고 전문적이었어요.", rating: 5 },
];

function findPreset(profession: string): Preset | null {
  const p = profession.replace(/\s+/g, "");
  for (const preset of PRESETS) {
    if (preset.aliases.some((a) => p.includes(a.replace(/\s+/g, "")))) {
      return preset;
    }
  }
  return null;
}

function genericProblems(label: string): string[] {
  return [
    `어디에, 누구에게 ${label} 관련 일을 맡겨야 할지 막막하신가요?`,
    "생각보다 복잡한 절차에 벌써 지치셨나요?",
    "비용이 얼마나 나올지 몰라 걱정되시나요?",
    "제대로 된 설명 없이 진행될까 불안하신가요?",
  ];
}

function genericServices(label: string): Item[] {
  return [
    { title: "정확한 진단", desc: `상황을 꼼꼼히 듣고 ${label} 관점에서 무엇이 핵심인지 명확하게 짚어드립니다.` },
    { title: "맞춤 해결책", desc: "뻔한 답이 아니라, 고객님 상황에 딱 맞는 현실적인 방법을 제안합니다." },
    { title: "끝까지 책임", desc: "진행 과정을 투명하게 공유하고, 마무리까지 함께합니다." },
    { title: "사후 관리", desc: "끝난 뒤에도 궁금한 점은 언제든 편하게 문의하실 수 있습니다." },
  ];
}

function genericWhy(label: string, strengths: string[]): Item[] {
  const base: Item[] = [
    { title: "풍부한 경험", desc: `수많은 ${label} 사례를 다뤄온 경험으로 시행착오를 줄여드립니다.` },
    { title: "투명한 비용", desc: "진행 전에 예상 비용을 명확히 알려드려 부담을 줄입니다." },
    { title: "빠른 응대", desc: "문의 주시면 최대한 빠르게 연락드립니다." },
    { title: "1:1 밀착 상담", desc: "고객님 한 분 한 분의 상황에 맞춰 세심하게 챙깁니다." },
  ];
  const extra: Item[] = strengths
    .filter((s) => s.trim())
    .slice(0, 3)
    .map((s) => ({ title: "차별점", desc: s.trim() }));
  return [...extra, ...base].slice(0, 4);
}

function genericFaq(label: string, consultWord: string): Faq[] {
  return [
    { q: `${consultWord}은 어떻게 진행되나요?`, a: "전화나 카카오톡으로 편하게 연락 주시면, 상황을 듣고 어떻게 도와드릴 수 있는지 안내해 드립니다." },
    { q: "비용은 어떻게 되나요?", a: "상황에 따라 다르며, 진행 전에 예상 비용을 투명하게 알려드립니다. 상담만으로 비용이 청구되지 않습니다." },
    { q: "얼마나 걸리나요?", a: `사안에 따라 다르지만, 상담 시 예상 일정을 함께 안내해 드립니다.` },
    { q: "지금 바로 상담할 수 있나요?", a: "네, 아래 연락처로 문의 주시면 가능한 빠르게 도와드리겠습니다." },
  ];
}

/** 입력값으로 완성된 상세페이지 내용을 생성 */
export function generatePage(input: GenerateInput): PageContent {
  const label = (input.profession || "전문가").trim() || "전문가";
  const preset = findPreset(label);
  const displayLabel = preset?.label ?? label;
  const consultWord = preset?.consultWord ?? "상담";
  const accent = input.accent || "#2563eb";
  const businessName = (input.businessName || "").trim();
  const region = (input.region || "").trim();
  const years = (input.years || "").trim();
  const strengths = input.strengths ?? [];

  const heroSubtitle = preset?.heroSubtitle
    ? preset.heroSubtitle(displayLabel)
    : `${displayLabel} 관련 고민, 혼자 끙끙 앓지 마세요. 처음부터 끝까지 책임지고 도와드립니다. 지금 바로 부담 없이 ${consultWord} 받아보세요.`;

  const stats: Stat[] = [
    { value: years ? `${years}${/^\d+$/.test(years) ? "년+" : ""}` : "다년간", label: "분야 경력" },
    { value: "1:1", label: "맞춤 상담" },
    { value: "당일", label: "빠른 연락" },
  ];

  const services = preset?.services ?? genericServices(displayLabel);
  const why = genericWhy(displayLabel, strengths);
  const problems = preset?.problems ?? genericProblems(displayLabel);
  const faq = preset?.faq ?? genericFaq(displayLabel, consultWord);
  const testimonials = preset?.testimonials ?? GENERIC_TESTIMONIALS;

  const kickerParts = [region, `${displayLabel} 전문`].filter(Boolean);

  return {
    accent,
    professionLabel: displayLabel,
    businessName: businessName || `${displayLabel} 상담`,
    hero: {
      kicker: kickerParts.join(" · "),
      title: businessName || `믿고 맡기는 ${displayLabel}`,
      highlight: businessName ? `${displayLabel} 전문 상담` : "지금 바로 상담하세요",
      subtitle: heroSubtitle,
      ctaPrimary: `무료 ${consultWord} 신청`,
      badges: ["빠른 상담", "합리적 비용", "풍부한 경험"],
    },
    stats,
    problems: {
      title: "이런 고민, 있으시죠?",
      subtitle: "하나라도 해당된다면 지금 바로 도와드릴 수 있습니다.",
      items: problems,
    },
    services: {
      title: "이렇게 도와드립니다",
      subtitle: `${displayLabel}가 직접 처음부터 끝까지 책임집니다.`,
      items: services,
    },
    why: {
      title: `왜 ${businessName || "저희"}를 선택해야 할까요?`,
      subtitle: "고객이 다시 찾고, 추천하는 이유가 있습니다.",
      items: why,
    },
    process: {
      title: "이렇게 진행됩니다",
      subtitle: "복잡할 것 없어요. 연락 한 번이면 시작됩니다.",
      steps: [
        { title: "문의 · 상담 신청", desc: "전화나 카카오톡으로 편하게 남겨주세요." },
        { title: `무료 ${consultWord}`, desc: "상황을 듣고 어떻게 도와드릴지 정확히 알려드립니다." },
        { title: "맞춤 플랜 제안", desc: "예상 비용과 일정을 투명하게 안내합니다." },
        { title: "진행 및 마무리", desc: "믿고 맡기시면 결과로 보답합니다." },
      ],
    },
    testimonials: {
      title: "고객 후기",
      items: testimonials,
    },
    faq: {
      title: "자주 묻는 질문",
      items: faq,
    },
    finalCta: {
      title: "지금 바로 상담받아 보세요",
      subtitle: "고민은 짧게, 해결은 확실하게. 부담 없이 편하게 연락 주세요.",
      note: region ? `${region} 및 인근 지역 상담 가능` : "전국 상담 가능",
    },
    contact: {
      phone: (input.phone || "").trim(),
      kakao: (input.kakao || "").trim(),
    },
  };
}

/** UI 에서 보여줄 추천 직업 칩 */
export const PROFESSION_SUGGESTIONS = [
  "변호사",
  "세무사",
  "노무사",
  "손해사정사",
  "공인중개사",
  "인테리어",
  "건축사",
  "변리사",
  "한의원",
  "심리상담",
];
