import { Card, Title, Group, Box, Tooltip, Text, SimpleGrid } from '@mantine/core';
import { IconChartPie } from '@tabler/icons-react';
import { SectorInfo } from '../types/api';

interface SectorHeatmapProps {
    sectors: SectorInfo[] | null;
}

export function SectorHeatmap({ sectors }: SectorHeatmapProps) {
    if (!sectors) return null;

    // 등락률에 따른 배경색 결정
    const getBackgroundColor = (rate: number) => {
        if (rate >= 3) return 'rgba(34, 197, 94, 0.9)'; // 진한 초록
        if (rate >= 1) return 'rgba(34, 197, 94, 0.6)'; // 초록
        if (rate > 0) return 'rgba(34, 197, 94, 0.3)';  // 연한 초록
        if (rate === 0) return 'rgba(128, 128, 128, 0.3)'; // 회색
        if (rate > -1) return 'rgba(239, 68, 68, 0.3)';  // 연한 빨강
        if (rate > -3) return 'rgba(239, 68, 68, 0.6)';  // 빨강
        return 'rgba(239, 68, 68, 0.9)';                 // 진한 빨강
    };

    return (
        <Card shadow="sm" p="lg" radius="md" withBorder>
            <Group mb="md">
                <IconChartPie size={20} className="text-purple-400" />
                <Title order={4}>섹터별 등락 현황</Title>
            </Group>

            <SimpleGrid cols={{ base: 2, sm: 3, md: 6 }} spacing="sm">
                {sectors.map((sector) => (
                    <Box
                        key={sector.name}
                        p="md"
                        style={{
                            backgroundColor: getBackgroundColor(sector.change_rate),
                            borderRadius: '8px',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'center',
                            alignItems: 'center',
                            textAlign: 'center',
                            height: '100px',
                            transition: 'transform 0.2s',
                            cursor: 'default'
                        }}
                    >
                        <Text size="sm" fw={700} c="white" style={{ textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}>
                            {sector.name}
                        </Text>
                        <Text size="lg" fw={800} c="white" mt={4} style={{ textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}>
                            {sector.change_rate > 0 ? '+' : ''}{sector.change_rate}%
                        </Text>
                        <Text size="xs" c="white" mt={2} style={{ opacity: 0.8 }}>
                            {sector.volume}
                        </Text>
                    </Box>
                ))}
            </SimpleGrid>
        </Card>
    );
}
