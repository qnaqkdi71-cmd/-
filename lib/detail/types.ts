// 전문직 상세페이지 데이터 구조
// 하나의 상세페이지는 아래 PageContent 로 표현되고,
// 미리보기(DetailPagePreview)와 HTML 내보내기(exportHtml)가 모두 이 값을 씁니다.

export type Tone = "trust" | "friendly" | "premium";

/** 사용자가 입력하는 값 (대부분 선택 입력) */
export interface GenerateInput {
  /** 직업/전문분야 (필수). 예: "변호사", "이혼 전문 변호사", "인테리어" */
  profession: string;
  /** 상호명 또는 대표자 이름. 예: "OO법률사무소", "김세무사" */
  businessName?: string;
  /** 지역. 예: "서울 강남", "부산" */
  region?: string;
  /** 경력(년). 숫자 또는 자유 텍스트 */
  years?: string;
  /** 전화번호 */
  phone?: string;
  /** 카카오톡 채널/오픈채팅 링크 또는 아이디 */
  kakao?: string;
  /** 직접 강조하고 싶은 강점들 (한 줄에 하나) */
  strengths?: string[];
  /** 강조색 (HEX) */
  accent?: string;
  /** 말투/분위기 */
  tone?: Tone;
}

export interface Stat {
  value: string;
  label: string;
}

export interface Item {
  title: string;
  desc: string;
}

export interface Step {
  title: string;
  desc: string;
}

export interface Testimonial {
  name: string;
  text: string;
  rating: number;
}

export interface Faq {
  q: string;
  a: string;
}

/** 완성된 상세페이지 내용 */
export interface PageContent {
  accent: string;
  professionLabel: string;
  businessName: string;

  hero: {
    kicker: string;
    title: string;
    highlight: string;
    subtitle: string;
    ctaPrimary: string;
    badges: string[];
  };

  stats: Stat[];

  problems: {
    title: string;
    subtitle: string;
    items: string[];
  };

  services: {
    title: string;
    subtitle: string;
    items: Item[];
  };

  why: {
    title: string;
    subtitle: string;
    items: Item[];
  };

  process: {
    title: string;
    subtitle: string;
    steps: Step[];
  };

  testimonials: {
    title: string;
    items: Testimonial[];
  };

  faq: {
    title: string;
    items: Faq[];
  };

  finalCta: {
    title: string;
    subtitle: string;
    note: string;
  };

  contact: {
    phone: string;
    kakao: string;
  };
}
