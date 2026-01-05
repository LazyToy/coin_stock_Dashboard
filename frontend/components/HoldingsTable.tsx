"use client";

import { Paper, Table, Text, Group, Badge, Stack, Skeleton } from "@mantine/core";
import { IconTrendingUp, IconTrendingDown, IconCoins } from "@tabler/icons-react";
import { UpbitHolding, BinanceHolding } from "@/types/api";

interface HoldingsTableProps {
    exchange: "upbit" | "binance";
    holdings: UpbitHolding[] | BinanceHolding[] | null;
    loading?: boolean;
}

export function HoldingsTable({ exchange, holdings, loading }: HoldingsTableProps) {
    const isUpbit = exchange === "upbit";
    const currency = isUpbit ? "KRW" : "USDT";
    const exchangeName = isUpbit ? "업비트" : "바이낸스";
    const gradientClass = isUpbit ? "upbit-gradient" : "binance-gradient";

    const formatNumber = (num: number, decimals: number = 2) => {
        if (isUpbit && decimals === 0) {
            return new Intl.NumberFormat("ko-KR").format(Math.round(num));
        }
        return new Intl.NumberFormat("en-US", {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        }).format(num);
    };

    const formatQuantity = (num: number) => {
        if (num >= 1) {
            return formatNumber(num, 4);
        }
        return num.toFixed(8);
    };

    if (loading) {
        return (
            <Paper className="glass-card" p="xl" radius="lg">
                <Stack gap="md">
                    <Skeleton height={24} width="50%" />
                    {[1, 2, 3].map((i) => (
                        <Skeleton key={i} height={48} />
                    ))}
                </Stack>
            </Paper>
        );
    }

    const totalEval = holdings?.reduce((sum, h) => sum + h.eval_amount, 0) || 0;

    return (
        <Paper className="glass-card animate-fadeIn" p="xl" radius="lg">
            <Stack gap="md">
                {/* Header */}
                <Group justify="space-between" align="center">
                    <Group gap="xs">
                        <div
                            className={gradientClass}
                            style={{
                                width: 8,
                                height: 32,
                                borderRadius: 4,
                            }}
                        />
                        <Text fw={600} size="lg" c="dimmed">
                            {exchangeName} 보유 코인
                        </Text>
                    </Group>
                    <IconCoins size={24} style={{ opacity: 0.5 }} />
                </Group>

                {/* Table */}
                {holdings && holdings.length > 0 ? (
                    <>
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
                                    <Table.Th>코인</Table.Th>
                                    <Table.Th style={{ textAlign: "right" }}>보유량</Table.Th>
                                    <Table.Th style={{ textAlign: "right" }}>현재가</Table.Th>
                                    <Table.Th style={{ textAlign: "right" }}>평가금액</Table.Th>
                                    {isUpbit && <Table.Th style={{ textAlign: "right" }}>수익률</Table.Th>}
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {holdings.map((holding, index) => {
                                    const symbol = isUpbit
                                        ? (holding as UpbitHolding).currency
                                        : (holding as BinanceHolding).asset;
                                    const profitRate = isUpbit ? (holding as UpbitHolding).profit_rate : null;
                                    const isProfit = profitRate !== null && profitRate >= 0;

                                    return (
                                        <Table.Tr key={index}>
                                            <Table.Td>
                                                <Badge
                                                    variant="light"
                                                    color={isUpbit ? "cyan" : "yellow"}
                                                    size="lg"
                                                >
                                                    {symbol}
                                                </Badge>
                                            </Table.Td>
                                            <Table.Td style={{ textAlign: "right" }}>
                                                <Text size="sm" fw={500}>
                                                    {formatQuantity(holding.total)}
                                                </Text>
                                            </Table.Td>
                                            <Table.Td style={{ textAlign: "right" }}>
                                                <Text size="sm">
                                                    {holding.current_price
                                                        ? `${formatNumber(holding.current_price, isUpbit ? 0 : 4)} ${currency}`
                                                        : "-"}
                                                </Text>
                                            </Table.Td>
                                            <Table.Td style={{ textAlign: "right" }}>
                                                <Text size="sm" fw={500}>
                                                    {formatNumber(holding.eval_amount, isUpbit ? 0 : 2)} {currency}
                                                </Text>
                                            </Table.Td>
                                            {isUpbit && profitRate !== null && (
                                                <Table.Td style={{ textAlign: "right" }}>
                                                    <Group gap={4} justify="flex-end">
                                                        {isProfit ? (
                                                            <IconTrendingUp size={16} className="price-up" />
                                                        ) : (
                                                            <IconTrendingDown size={16} className="price-down" />
                                                        )}
                                                        <Text
                                                            size="sm"
                                                            fw={600}
                                                            className={isProfit ? "price-up" : "price-down"}
                                                        >
                                                            {profitRate >= 0 ? "+" : ""}
                                                            {profitRate.toFixed(2)}%
                                                        </Text>
                                                    </Group>
                                                </Table.Td>
                                            )}
                                        </Table.Tr>
                                    );
                                })}
                            </Table.Tbody>
                        </Table>

                        {/* Total */}
                        <Group
                            justify="space-between"
                            p="md"
                            style={{
                                background: "rgba(255,255,255,0.03)",
                                borderRadius: 8,
                            }}
                        >
                            <Text fw={500} c="dimmed">
                                총 평가 금액
                            </Text>
                            <Text
                                fw={700}
                                size="lg"
                                style={{
                                    background: isUpbit
                                        ? "linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)"
                                        : "linear-gradient(135deg, #f0b90b 0%, #f5d442 100%)",
                                    WebkitBackgroundClip: "text",
                                    WebkitTextFillColor: "transparent",
                                }}
                            >
                                {formatNumber(totalEval, isUpbit ? 0 : 2)} {currency}
                            </Text>
                        </Group>
                    </>
                ) : (
                    <Text c="dimmed" ta="center" py="xl">
                        보유 중인 코인이 없습니다
                    </Text>
                )}
            </Stack>
        </Paper>
    );
}
