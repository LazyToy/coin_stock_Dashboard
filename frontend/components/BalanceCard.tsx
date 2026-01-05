"use client";

import { Paper, Text, Group, Stack, RingProgress, Skeleton } from "@mantine/core";
import { IconWallet, IconLock, IconCoin } from "@tabler/icons-react";

interface BalanceCardProps {
    exchange: "upbit" | "binance";
    total: number;
    available: number;
    locked: number;
    loading?: boolean;
}

export function BalanceCard({ exchange, total, available, locked, loading }: BalanceCardProps) {
    const isUpbit = exchange === "upbit";
    const currency = isUpbit ? "KRW" : "USDT";
    const gradientClass = isUpbit ? "upbit-gradient" : "binance-gradient";
    const exchangeName = isUpbit ? "업비트" : "바이낸스";

    const availablePercent = total > 0 ? (available / total) * 100 : 100;

    const formatNumber = (num: number) => {
        if (isUpbit) {
            return new Intl.NumberFormat("ko-KR").format(Math.round(num));
        }
        return new Intl.NumberFormat("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(num);
    };

    if (loading) {
        return (
            <Paper className="glass-card hover-lift" p="xl" radius="lg">
                <Stack gap="md">
                    <Skeleton height={24} width="40%" />
                    <Skeleton height={40} width="60%" />
                    <Group>
                        <Skeleton height={60} width={60} circle />
                        <Stack gap="xs" style={{ flex: 1 }}>
                            <Skeleton height={16} width="80%" />
                            <Skeleton height={16} width="60%" />
                        </Stack>
                    </Group>
                </Stack>
            </Paper>
        );
    }

    return (
        <Paper className="glass-card hover-lift animate-fadeIn" p="xl" radius="lg">
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
                            {exchangeName} 잔액
                        </Text>
                    </Group>
                    <IconWallet size={24} style={{ opacity: 0.5 }} />
                </Group>

                {/* Total Balance */}
                <Text
                    fw={700}
                    size="xl"
                    style={{
                        fontSize: "2rem",
                        background: isUpbit
                            ? "linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)"
                            : "linear-gradient(135deg, #f0b90b 0%, #f5d442 100%)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                    }}
                >
                    {formatNumber(total)} {currency}
                </Text>

                {/* Details with Ring Progress */}
                <Group gap="lg" mt="sm">
                    <RingProgress
                        size={80}
                        thickness={8}
                        roundCaps
                        sections={[
                            { value: availablePercent, color: isUpbit ? "cyan" : "yellow" },
                        ]}
                        label={
                            <Text size="xs" ta="center" fw={500}>
                                {availablePercent.toFixed(0)}%
                            </Text>
                        }
                    />

                    <Stack gap="xs" style={{ flex: 1 }}>
                        <Group gap="xs">
                            <IconCoin size={16} style={{ color: "var(--mantine-color-green-5)" }} />
                            <Text size="sm" c="dimmed">사용 가능</Text>
                            <Text size="sm" fw={500} ml="auto">
                                {formatNumber(available)} {currency}
                            </Text>
                        </Group>
                        <Group gap="xs">
                            <IconLock size={16} style={{ color: "var(--mantine-color-red-5)" }} />
                            <Text size="sm" c="dimmed">거래 중</Text>
                            <Text size="sm" fw={500} ml="auto">
                                {formatNumber(locked)} {currency}
                            </Text>
                        </Group>
                    </Stack>
                </Group>
            </Stack>
        </Paper>
    );
}
