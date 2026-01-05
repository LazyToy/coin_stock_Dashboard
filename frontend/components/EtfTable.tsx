import { Paper, Table, Text, Group, Badge, Stack, Skeleton } from "@mantine/core";
import { IconFlame } from "@tabler/icons-react";
import { ETFItem } from "@/types/api";

interface EtfTableProps {
    etfs: ETFItem[] | null;
    loading?: boolean;
}

export function EtfTable({ etfs, loading }: EtfTableProps) {
    // 통일된 숫자 포맷
    const formatPrice = (num: number) => {
        return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(num);
    };

    const formatVolume = (num: number) => {
        if (num >= 1000000000) return `${(num / 1000000000).toFixed(2)}B`;
        if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`;
        return num.toLocaleString();
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

    if (!etfs) return null;

    return (
        <Paper className="glass-card animate-fadeIn" p="xl" radius="lg">
            <Stack gap="md">
                {/* Header - StockVolumeTable Style Match */}
                <Group justify="space-between" align="center">
                    <Group gap="xs">
                        <div
                            style={{
                                width: 8,
                                height: 32,
                                borderRadius: 4,
                                background: "linear-gradient(135deg, #FF9500 0%, #FFCC00 100%)", // Unique Orange Color for ETF
                            }}
                        />
                        <Text fw={600} size="lg" c="dimmed">
                            ETF 거래량 TOP 10
                        </Text>
                    </Group>
                    <IconFlame size={24} style={{ opacity: 0.5, color: "#ff9f0a" }} />
                </Group>

                {/* Table */}
                <Table
                    striped
                    highlightOnHover
                    withTableBorder={false}
                    verticalSpacing="xs"
                    styles={{
                        tr: {
                            borderBottom: "1px solid rgba(255,255,255,0.05)"
                        },
                        th: {
                            color: "var(--mantine-color-dimmed)",
                            fontWeight: 500,
                            fontSize: "0.8rem"
                        },
                    }}
                >
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>종목</Table.Th>
                            <Table.Th style={{ textAlign: "right" }}>가격 (USD)</Table.Th>
                            <Table.Th style={{ textAlign: "right" }}>거래량</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {etfs.map((etf, index) => {
                            const isPositive = etf.change_rate >= 0;
                            return (
                                <Table.Tr key={index}>
                                    <Table.Td>
                                        <Group gap="sm">
                                            <Badge
                                                size="sm"
                                                color="gray"
                                                variant="light"
                                                circle
                                                style={{ width: 24, height: 24, fontSize: 10, minWidth: 24 }}
                                            >
                                                {index + 1}
                                            </Badge>
                                            <Stack gap={0}>
                                                <Text size="sm" fw={700} c="white">{etf.symbol || etf.code}</Text>
                                                <Text size="xs" c="dimmed" lineClamp={1} style={{ maxWidth: 120 }}>{etf.name}</Text>
                                            </Stack>
                                        </Group>
                                    </Table.Td>
                                    <Table.Td style={{ textAlign: "right" }}>
                                        <Text size="sm" fw={600} c="white">{formatPrice(etf.current_price)}</Text>
                                        <Text size="xs" c={isPositive ? "teal" : "red"}>
                                            {isPositive ? "+" : ""}{etf.change_rate.toFixed(2)}%
                                        </Text>
                                    </Table.Td>
                                    <Table.Td style={{ textAlign: "right" }}>
                                        <Text size="sm" c="dimmed">{formatVolume(etf.trade_volume)}</Text>
                                    </Table.Td>
                                </Table.Tr>
                            );
                        })}
                    </Table.Tbody>
                </Table>
            </Stack>
        </Paper>
    );
}
