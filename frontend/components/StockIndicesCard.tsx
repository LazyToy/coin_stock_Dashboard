import { Paper, Title, Grid, Text, Group, ThemeIcon, Card } from '@mantine/core';
import { IconChartArrowsVertical, IconTrendingUp, IconTrendingDown, IconMinus } from '@tabler/icons-react';
import { StockIndex } from '../types/api';

interface StockIndicesCardProps {
    indices: StockIndex[] | null;
}

export function StockIndicesCard({ indices }: StockIndicesCardProps) {
    if (!indices || indices.length === 0) {
        return null; // 데이터가 없으면 표시하지 않음
    }

    return (
        <Card shadow="sm" p="lg" radius="md" withBorder>
            <Group mb="md">
                <IconChartArrowsVertical size={20} className="text-blue-400" />
                <Title order={4}>주요 지수 현황</Title>
            </Group>

            <Grid>
                {indices.map((index) => {
                    const isPositive = index.change_rate > 0;
                    const isZero = index.change_rate === 0;
                    const color = isPositive ? 'green' : isZero ? 'gray' : 'red';
                    const Icon = isPositive ? IconTrendingUp : isZero ? IconMinus : IconTrendingDown;

                    return (
                        <Grid.Col key={index.symbol} span={{ base: 6, sm: 3, md: 2.4 }}>
                            <Paper p="sm" radius="sm" bg="rgba(255, 255, 255, 0.03)">
                                <Text size="xs" c="dimmed" fw={700} tt="uppercase">
                                    {index.name}
                                </Text>
                                <Group gap={5} mt={5} align="flex-end">
                                    <Text size="lg" fw={700}>
                                        {index.current_price.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                                    </Text>
                                </Group>
                                <Group gap={4} mt={3}>
                                    <ThemeIcon size="xs" color={color} variant="transparent">
                                        <Icon size={12} />
                                    </ThemeIcon>
                                    <Text size="xs" c={isPositive ? 'teal' : isZero ? 'gray' : 'red'} fw={500}>
                                        {index.change > 0 ? '+' : ''}{index.change.toFixed(2)} ({index.change > 0 ? '+' : ''}{index.change_rate.toFixed(2)}%)
                                    </Text>
                                </Group>
                            </Paper>
                        </Grid.Col>
                    );
                })}
            </Grid>
        </Card>
    );
}
