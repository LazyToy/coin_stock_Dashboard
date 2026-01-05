"use client";

import { Paper, Table, Text, Group, Badge, Stack, Skeleton } from "@mantine/core";
import { IconTrendingUp, IconTrendingDown, IconFlame } from "@tabler/icons-react";
import { UpbitTopCoin, BinanceTopCoin } from "@/types/api";

interface TopVolumeTableProps {
    exchange: "upbit" | "binance";
    coins: UpbitTopCoin[] | BinanceTopCoin[] | null;
    loading?: boolean;
}

export function TopVolumeTable({ exchange, coins, loading }: TopVolumeTableProps) {
    const isUpbit = exchange === "upbit";
    const exchangeName = isUpbit ? "업비트" : "바이낸스";
    const gradientClass = isUpbit ? "upbit-gradient" : "binance-gradient";

    // 통일된 숫자 포맷 함수 - 모두 KRW 기준
    const formatKRW = (num: number) => {
        return new Intl.NumberFormat("ko-KR").format(Math.round(num));
    };

    // 통일된 거래대금 포맷 함수 - 모두 억 KRW 단위
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
                            className={gradientClass}
                            style={{
                                width: 8,
                                height: 32,
                                borderRadius: 4,
                            }}
                        />
                        <Text fw={600} size="lg" c="dimmed">
                            {exchangeName} 거래량 TOP 10
                        </Text>
                    </Group>
                    <IconFlame size={24} style={{ opacity: 0.5, color: "#ff6b6b" }} />
                </Group>

                {/* Table - 통일된 UI */}
                {coins && coins.length > 0 ? (
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
                                <Table.Th>코인</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>현재가</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>변동률</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>거래대금</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {coins.map((coin, index) => {
                                let symbol: string;
                                let name: string;
                                let currentPriceKRW: number;
                                let changeRate: number;
                                let tradePriceKRW: number;

                                if (isUpbit) {
                                    const upbitCoin = coin as UpbitTopCoin;
                                    symbol = upbitCoin.market.replace("KRW-", "");
                                    name = upbitCoin.korean_name;
                                    currentPriceKRW = upbitCoin.current_price;
                                    changeRate = upbitCoin.change_rate;
                                    tradePriceKRW = upbitCoin.trade_price;
                                } else {
                                    // 바이낸스 - KRW 변환된 값 사용
                                    const binanceCoin = coin as BinanceTopCoin;
                                    symbol = binanceCoin.base_asset;
                                    name = symbol; // 바이낸스는 한글명 없음
                                    currentPriceKRW = binanceCoin.current_price_krw;
                                    changeRate = binanceCoin.price_change_percent;
                                    tradePriceKRW = binanceCoin.quote_volume_krw;
                                }

                                const isPositive = changeRate >= 0;

                                return (
                                    <Table.Tr key={index}>
                                        {/* 순위 */}
                                        <Table.Td>
                                            <Badge
                                                variant="filled"
                                                size="sm"
                                                color={index < 3 ? "violet" : "gray"}
                                                style={{
                                                    minWidth: 28,
                                                }}
                                            >
                                                {index + 1}
                                            </Badge>
                                        </Table.Td>

                                        {/* 코인명 - 통일된 형식 */}
                                        <Table.Td>
                                            <Stack gap={0}>
                                                <Text size="sm" fw={600}>
                                                    {symbol}
                                                </Text>
                                                <Text size="xs" c="dimmed">
                                                    {isUpbit ? name : symbol}
                                                </Text>
                                            </Stack>
                                        </Table.Td>

                                        {/* 현재가 - 모두 KRW */}
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

                                        {/* 거래대금 - 모두 억 KRW */}
                                        <Table.Td style={{ textAlign: "right" }}>
                                            <Text size="sm" c="dimmed">
                                                {formatVolumeKRW(tradePriceKRW)} KRW
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
