"use client";

import { Paper, Table, Text, Group, Badge, Stack, Skeleton } from "@mantine/core";
import { IconTrendingUp, IconTrendingDown, IconFlame } from "@tabler/icons-react";
import { KoreaStock, USStock } from "@/types/api";

interface StockVolumeTableProps {
    market: "kospi" | "kosdaq" | "us";
    stocks: KoreaStock[] | USStock[] | null;
    loading?: boolean;
    onStockClick?: (name: string) => void;
}

export function StockVolumeTable({ market, stocks, loading, onStockClick }: StockVolumeTableProps) {
    const isUS = market === "us";

    const marketConfig = {
        kospi: {
            name: "코스피",
            gradientClass: "kospi-gradient",
        },
        kosdaq: {
            name: "코스닥",
            gradientClass: "kosdaq-gradient",
        },
        us: {
            name: "미국 주식",
            gradientClass: "us-gradient",
        },
    };

    const config = marketConfig[market];

    // 통일된 숫자 포맷 - KRW
    const formatKRW = (num: number) => {
        return new Intl.NumberFormat("ko-KR").format(Math.round(num));
    };

    // 거래대금 포맷 - 억 KRW
    const formatVolumeKRW = (num: number) => {
        return `${(num / 100000000).toFixed(2)}억`;
    };

    if (loading) {
        return (
            <Paper className="glass-card" p="xl" radius="lg">
                <Stack gap="md">
                    <Skeleton height={24} width="60%" />
                    {[1, 2, 3, 4, 5].map((i) => (
                        <Skeleton key={i} height={40} />
                    ))}
                </Stack>
            </Paper>
        );
    }

    return (
        <Paper className="glass-card animate-fadeIn" p="xl" radius="lg">
            <Stack gap="md">
                {/* Header */}
                <Group justify="space-between" align="center">
                    <Group gap="xs">
                        <div
                            style={{
                                width: 8,
                                height: 32,
                                borderRadius: 4,
                                background: market === "kospi"
                                    ? "linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)"
                                    : market === "kosdaq"
                                        ? "linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)"
                                        : "linear-gradient(135deg, #3498db 0%, #2980b9 100%)",
                            }}
                        />
                        <Text fw={600} size="lg" c="dimmed">
                            {config.name} 거래량 TOP 10
                        </Text>
                    </Group>
                    <IconFlame size={24} style={{ opacity: 0.5, color: "#ff6b6b" }} />
                </Group>

                {/* Table */}
                {stocks && stocks.length > 0 ? (
                    <Table
                        striped
                        highlightOnHover
                        withTableBorder={false}
                        styles={{
                            tr: {
                                borderBottom: "1px solid rgba(255,255,255,0.05)",
                            },
                            th: {
                                color: "var(--mantine-color-dimmed)",
                                fontWeight: 500,
                                fontSize: "0.8rem",
                            },
                        }}
                    >
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>#</Table.Th>
                                <Table.Th>종목</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>현재가</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>변동률</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>거래대금</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {stocks.map((stock, index) => {
                                let code: string;
                                let name: string;
                                let currentPriceKRW: number;
                                let changeRate: number;
                                let tradeValueKRW: number;

                                if (isUS) {
                                    const usStock = stock as USStock;
                                    code = usStock.symbol;
                                    name = usStock.name;
                                    currentPriceKRW = usStock.current_price_krw;
                                    changeRate = usStock.change_rate;
                                    tradeValueKRW = usStock.trade_value_krw;
                                } else {
                                    const krStock = stock as KoreaStock;
                                    code = krStock.code;
                                    name = krStock.name;
                                    currentPriceKRW = krStock.current_price;
                                    changeRate = krStock.change_rate;
                                    tradeValueKRW = krStock.trade_value;
                                }

                                const isPositive = changeRate >= 0;

                                return (
                                    <Table.Tr
                                        key={index}
                                        onClick={() => onStockClick && onStockClick(isUS ? `${code} ${name}` : name)}
                                        style={{ cursor: "pointer", transition: "background-color 0.2s" }}
                                    >
                                        {/* 순위 */}
                                        <Table.Td>
                                            <Badge
                                                variant="filled"
                                                size="sm"
                                                color={index < 3 ? "violet" : "gray"}
                                                style={{ minWidth: 28 }}
                                            >
                                                {index + 1}
                                            </Badge>
                                        </Table.Td>

                                        {/* 종목명 */}
                                        <Table.Td>
                                            <Stack gap={0}>
                                                <Text size="sm" fw={600}>
                                                    {isUS ? code : name}
                                                </Text>
                                                <Text size="xs" c="dimmed">
                                                    {isUS ? name : code}
                                                </Text>
                                            </Stack>
                                        </Table.Td>

                                        {/* 현재가 - KRW */}
                                        <Table.Td style={{ textAlign: "right" }}>
                                            <Text size="sm" fw={500}>
                                                {formatKRW(currentPriceKRW)} KRW
                                            </Text>
                                        </Table.Td>

                                        {/* 변동률 */}
                                        <Table.Td style={{ textAlign: "right" }}>
                                            <Group gap={4} justify="flex-end">
                                                {isPositive ? (
                                                    <IconTrendingUp size={16} className="price-up" />
                                                ) : (
                                                    <IconTrendingDown size={16} className="price-down" />
                                                )}
                                                <Text
                                                    size="sm"
                                                    fw={600}
                                                    className={isPositive ? "price-up" : "price-down"}
                                                >
                                                    {isPositive ? "+" : ""}
                                                    {changeRate.toFixed(2)}%
                                                </Text>
                                            </Group>
                                        </Table.Td>

                                        {/* 거래대금 - 억 KRW */}
                                        <Table.Td style={{ textAlign: "right" }}>
                                            <Text size="sm" c="dimmed">
                                                {formatVolumeKRW(tradeValueKRW)} KRW
                                            </Text>
                                        </Table.Td>
                                    </Table.Tr>
                                );
                            })}
                        </Table.Tbody>
                    </Table>
                ) : (
                    <Text c="dimmed" ta="center" py="xl">
                        거래량 정보를 불러올 수 없습니다
                    </Text>
                )}
            </Stack>
        </Paper>
    );
}
