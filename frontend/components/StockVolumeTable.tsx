"use client";

import { Paper, Table, Text, Group, Stack, Skeleton } from "@mantine/core";
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
        kospi: { name: "KOSPI Top 10" },
        kosdaq: { name: "KOSDAQ Top 10" },
        us: { name: "US Stocks Top 10" },
    };

    const config = marketConfig[market];

    const formatKRW = (num: number) => new Intl.NumberFormat("ko-KR").format(Math.round(num));
    const formatVolumeKRW = (num: number) => `${(num / 100000000).toFixed(1)}억`;
    const formatUSD = (num: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(num);
    const formatVolumeUS = (num: number) => num >= 1000000 ? `${(num / 1000000).toFixed(1)}M` : num.toLocaleString();

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
        <Paper className="glass-card animate-fadeIn" p="lg" radius="lg">
            <Stack gap="lg">
                {/* Header */}
                <Group justify="space-between" align="center" mb="xs">
                    <Stack gap={2}>
                        <Text fw={600} size="xl" style={{ letterSpacing: '-0.025em' }}>
                            {config.name}
                        </Text>
                        <Text c="dimmed" size="xs">
                            Most active by volume
                        </Text>
                    </Stack>
                </Group>

                {/* Table */}
                {stocks && stocks.length > 0 ? (
                    <Table verticalSpacing="sm" withTableBorder={false} withRowBorders={true}>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th style={{ paddingLeft: 0 }}>Asset</Table.Th>
                                <Table.Th style={{ textAlign: "right" }}>Price</Table.Th>
                                <Table.Th style={{ textAlign: "right", paddingRight: 0 }}>Volume</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {stocks.map((stock, index) => {
                                const name = isUS ? (stock as USStock).symbol : (stock as KoreaStock).name;
                                const subName = isUS ? (stock as USStock).name : (stock as KoreaStock).code;
                                const price = isUS ? (stock as USStock).current_price : (stock as KoreaStock).current_price;
                                const change = isUS ? (stock as USStock).change_rate : (stock as KoreaStock).change_rate;
                                const volumeStr = isUS
                                    ? formatVolumeUS((stock as USStock).trade_volume)
                                    : formatVolumeKRW((stock as KoreaStock).trade_value);

                                const displayPrice = isUS ? formatUSD(price) : formatKRW(price);
                                const isPositive = change >= 0;

                                return (
                                    <Table.Tr
                                        key={index}
                                        style={{ cursor: "pointer" }}
                                        onClick={() => onStockClick && onStockClick(isUS ? subName : name)}
                                    >
                                        <Table.Td style={{ paddingLeft: 0 }}>
                                            <Group gap="sm">
                                                <div
                                                    style={{
                                                        width: 24,
                                                        height: 24,
                                                        background: 'rgba(255, 255, 255, 0.15)',
                                                        borderRadius: '50%',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        fontSize: 11,
                                                        fontWeight: 700,
                                                        color: '#FFF'
                                                    }}
                                                >
                                                    {index + 1}
                                                </div>
                                                <Stack gap={0}>
                                                    <Text size="sm" fw={600} c="white">{name}</Text>
                                                    <Text size="xs" c="dimmed" lineClamp={1} style={{ minWidth: 120 }}>{subName}</Text>
                                                </Stack>
                                            </Group>
                                        </Table.Td>
                                        <Table.Td style={{ textAlign: "right" }}>
                                            <Text size="sm" fw={500} c="white">{displayPrice}</Text>
                                            <Text size="xs" c={isPositive ? "#34C759" : "#FF3B30"} fw={600}>
                                                {isPositive ? "+" : ""}{change.toFixed(2)}%
                                            </Text>
                                        </Table.Td>
                                        <Table.Td style={{ textAlign: "right", paddingRight: 0 }}>
                                            <Text size="xs" c="dimmed">{volumeStr}</Text>
                                        </Table.Td>
                                    </Table.Tr>
                                );
                            })}
                        </Table.Tbody>
                    </Table>
                ) : (
                    <Text c="dimmed" ta="center" py="xl">No data available</Text>
                )}
            </Stack>
        </Paper>
    );
}
