// API 클라이언트

import { DashboardData, StockDashboardData } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchDashboard(): Promise<DashboardData> {
    const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
        cache: "no-store",
    });

    if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
    }

    return response.json();
}

export async function fetchStockDashboard(): Promise<StockDashboardData> {
    const response = await fetch(`${API_BASE_URL}/api/stock/dashboard`, {
        cache: "no-store",
    });

    if (!response.ok) {
        throw new Error("Failed to fetch stock dashboard data");
    }

    return response.json();
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function fetchUpbitBalance(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/upbit/balance`, {
        cache: "no-store",
    });
    return response.json();
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function fetchBinanceBalance(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/binance/balance`, {
        cache: "no-store",
    });
    return response.json();
}
