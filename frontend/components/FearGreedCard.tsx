import { Paper, Title, Group, Text, RingProgress, Center } from '@mantine/core';
import { IconGauge } from '@tabler/icons-react';
import { FearGreedIndex } from '../types/api';

interface FearGreedCardProps {
    data: FearGreedIndex | null;
}

export function FearGreedCard({ data }: FearGreedCardProps) {
    if (!data) return null;

    const value = data.value;
    // 색상 결정
    const getColor = (val: number) => {
        if (val < 25) return '#ff453a'; // Extreme Fear (Red)
        if (val < 45) return '#ff9f0a'; // Fear (Orange)
        if (val < 55) return '#8e8e93'; // Neutral (Gray)
        if (val < 75) return '#32d74b'; // Greed (Light Green)
        return '#30d158'; // Extreme Greed (Green)
    };

    const color = getColor(value);

    return (
        <Paper className="glass-card animate-fadeIn" p="lg" radius="xl" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Group mb="md">
                <IconGauge size={20} style={{ color: color }} />
                <Title order={4} style={{ fontFamily: 'system-ui' }}>공포 & 탐욕 지수</Title>
            </Group>

            <Center style={{ flex: 1 }}>
                <RingProgress
                    size={160}
                    thickness={16}
                    roundCaps
                    sections={[{ value: value, color: color }]}
                    label={
                        <Center>
                            <div style={{ textAlign: 'center' }}>
                                <Text fw={800} size="xl" style={{ fontSize: '2rem', lineHeight: 1 }}>
                                    {value}
                                </Text>
                                <Text size="xs" c="dimmed" fw={600} mt={4}>
                                    {data.value_classification}
                                </Text>
                            </div>
                        </Center>
                    }
                />
            </Center>

            <Text size="xs" c="dimmed" ta="center" mt="sm">
                업데이트: {new Date(data.timestamp * 1000).toLocaleDateString()}
            </Text>
        </Paper>
    );
}
