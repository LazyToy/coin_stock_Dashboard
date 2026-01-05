import { Paper, Table, Text, Group, Badge, Stack, Skeleton } from "@mantine/core";
import { ETFItem } from "@/types/api";

interface EtfTableProps {
    etfs: ETFItem[] | null;
    loading?: boolean;
}

export function EtfTable({ etfs, loading }: EtfTableProps) {
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
        <Paper className="glass-card animate-fadeIn" p="lg" radius="lg">
            <Stack gap="lg">
                {/* Header - Apple Style: Simple, Bold */}
                <Group justify="space-between" align="center" mb="xs">
                    <Stack gap={2}>
                        <Text fw={600} size="xl" style={{ letterSpacing: '-0.025em' }}>
                            Top ETFs
                        </Text>
                        <Text c="dimmed" size="xs">
                            Based on trading volume
                        </Text>
                    </Stack>
                </Group>

                {/* Table */}
                <Table
                    verticalSpacing="sm"
                    withTableBorder={false}
                    withRowBorders={true}
                >
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th style={{ paddingLeft: 0 }}>Symbol</Table.Th>
                            <Table.Th style={{ textAlign: "right" }}>Price</Table.Th>
                            <Table.Th style={{ textAlign: "right", paddingRight: 0 }}>Volume</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {etfs.map((etf, index) => {
                            const isPositive = etf.change_rate >= 0;
                            return (
                                <Table.Tr key={index}>
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
                                                <Text size="sm" fw={600}>{etf.symbol || etf.code}</Text>
                                                <Text size="xs" c="dimmed" lineClamp={1} style={{ maxWidth: 120 }}>{etf.name}</Text>
                                            </Stack>
                                        </Group>
                                    </Table.Td>
                                    <Table.Td style={{ textAlign: "right" }}>
                                        <Text size="sm" fw={500}>{formatPrice(etf.current_price)}</Text>
                                        <Text size="xs" c={isPositive ? "#34C759" : "#FF3B30"} fw={500}> {/* Apple Green/Red */}
                                            {isPositive ? "+" : ""}{etf.change_rate.toFixed(2)}%
                                        </Text>
                                    </Table.Td>
                                    <Table.Td style={{ textAlign: "right", paddingRight: 0 }}>
                                        <Text size="xs" c="dimmed">{formatVolume(etf.trade_volume)}</Text>
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
