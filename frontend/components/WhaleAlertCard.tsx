import { Paper, Title, Group, Text, Stack, ScrollArea, Avatar, ThemeIcon } from '@mantine/core';
import { IconBell, IconArrowRight, IconBuildingBank, IconWallet } from '@tabler/icons-react';
import { WhaleAlert } from '../types/api';

interface WhaleAlertCardProps {
    alerts: WhaleAlert[] | null;
}

export function WhaleAlertCard({ alerts }: WhaleAlertCardProps) {
    if (!alerts) return null;

    // Exchange Icon Mapping (Simple)
    const getIcon = (name: string) => {
        if (name.includes('Wallet')) return <IconWallet size={16} />;
        return <IconBuildingBank size={16} />;
    };

    return (
        <Paper className="glass-card animate-fadeIn" p="lg" radius="xl" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Group mb="md" justify="space-between">
                <Group>
                    <IconBell size={20} className="text-yellow-400" />
                    <Title order={4} style={{ fontFamily: 'system-ui' }}>실시간 고래 알림</Title>
                </Group>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#ff453a', boxShadow: '0 0 8px #ff453a' }} />
            </Group>

            <ScrollArea style={{ flex: 1, paddingRight: 10 }} scrollbarSize={6}>
                <Stack gap="xs">
                    {alerts.map((alert, index) => (
                        <Paper
                            key={index}
                            p="sm"
                            radius="lg"
                            bg="rgba(255,255,255,0.03)"
                            style={{
                                border: '1px solid rgba(255,255,255,0.05)',
                                transition: 'transform 0.2s',
                            }}
                            className="hover:bg-white/5"
                        >
                            <Group justify="space-between" align="start" wrap="nowrap">
                                <Stack gap={2}>
                                    <Text fw={700} size="sm" c="white">
                                        {alert.amount.toLocaleString()} {alert.coin}
                                    </Text>
                                    <Text size="xs" c="dimmed">
                                        ≈ ${alert.value_usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                                    </Text>
                                </Stack>
                                <Text size="xs" c="dimmed" style={{ whiteSpace: 'nowrap' }}>
                                    {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </Text>
                            </Group>

                            <Group mt="xs" align="center" gap={8} style={{ opacity: 0.8 }}>
                                <Group gap={4}>
                                    <ThemeIcon size="xs" variant="transparent" color="gray">
                                        {getIcon(alert.sender)}
                                    </ThemeIcon>
                                    <Text size="xs">{alert.sender}</Text>
                                </Group>
                                <IconArrowRight size={12} style={{ color: '#86868b' }} />
                                <Group gap={4}>
                                    <ThemeIcon size="xs" variant="transparent" color="gray">
                                        {getIcon(alert.receiver)}
                                    </ThemeIcon>
                                    <Text size="xs">{alert.receiver}</Text>
                                </Group>
                            </Group>
                        </Paper>
                    ))}
                </Stack>
            </ScrollArea>
        </Paper>
    );
}
