// API 타입 정의

export interface UpbitBalance {
    total_krw: number;
    available_krw: number;
    locked_krw: number;
}

export interface UpbitHolding {
    currency: string;
    balance: number;
    locked: number;
    total: number;
    avg_buy_price: number;
    current_price: number | null;
    eval_amount: number;
    profit_rate: number;
}

export interface UpbitTopCoin {
    market: string;
    korean_name: string;
    english_name: string;
    trade_volume: number;
    trade_price: number;
    current_price: number;
    change_rate: number;
}

export interface BinanceBalance {
    total_usdt: number;
    available_usdt: number;
    locked_usdt: number;
}

export interface BinanceHolding {
    asset: string;
    free: number;
    locked: number;
    total: number;
    current_price: number;
    eval_amount: number;
}

export interface BinanceTopCoin {
    symbol: string;
    base_asset: string;
    quote_volume: number;
    volume: number;
    current_price: number;
    price_change_percent: number;
    // KRW 변환 필드
    current_price_krw: number;
    quote_volume_krw: number;
}

export interface FearGreedIndex {
    value: number;
    value_classification: string;
    timestamp: number;
}

export interface WhaleAlert {
    coin: string;
    amount: number;
    sender: string;
    receiver: string;
    value_usd: number;
    timestamp: string;
}

export interface DashboardData {
    upbit_balance: UpbitBalance | null;
    upbit_holdings: UpbitHolding[] | null;
    upbit_top_volume: UpbitTopCoin[] | null;
    binance_balance: BinanceBalance | null;
    binance_holdings: BinanceHolding[] | null;
    binance_top_volume: BinanceTopCoin[] | null;
    fear_greed: FearGreedIndex | null;
    whale_alerts: WhaleAlert[] | null;
    last_updated: string;
}

// === 주식 타입 정의 ===

export interface KoreaStock {
    code: string;
    name: string;
    current_price: number;
    change_rate: number;
    trade_volume: number;
    trade_value: number; // KRW
}

export interface USStock {
    symbol: string;
    name: string;
    current_price: number; // USD
    change_rate: number;
    trade_volume: number;
    trade_value: number; // USD
    current_price_krw: number;
    trade_value_krw: number;
}

export interface ETFItem {
    symbol?: string;
    code?: string;
    name: string;
    current_price: number;
    change_rate: number;
    trade_volume: number;
    trade_value: number;
    current_price_krw?: number;
    trade_value_krw?: number;
}

export interface StockIndex {
    name: string;
    symbol: string;
    current_price: number;
    change: number;
    change_rate: number;
}

export interface SectorInfo {
    name: string;
    change_rate: number;
    volume: string;
}

export interface NewsItem {
    title: string;
    link: string;
    date: string;
    source: string;
}

export interface StockDashboardData {
    kospi_top: KoreaStock[] | null;
    kosdaq_top: KoreaStock[] | null;
    us_top: USStock[] | null;
    indices: StockIndex[] | null;
    sectors: SectorInfo[] | null;
    etf_ranking: ETFItem[] | null;
    last_updated: string;
}
