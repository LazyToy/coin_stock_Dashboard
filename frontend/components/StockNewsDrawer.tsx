import { Drawer, ScrollArea, Text, Card, Group, Badge, Stack, Loader, Center } from '@mantine/core';
import { IconNews } from '@tabler/icons-react';
import { NewsItem } from '../types/api';
import { useEffect, useState } from 'react';

interface StockNewsDrawerProps {
    opened: boolean;
    onClose: () => void;
    stockName: string | null;
}

export function StockNewsDrawer({ opened, onClose, stockName }: StockNewsDrawerProps) {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (opened && stockName) {
            setLoading(true);
            const query = encodeURIComponent(stockName);
            // 실제 구현에서는 API를 호출해야 하지만, 여기서는 예시로 fetch 로직을 구현
            // Dashboard.tsx나 api.ts에서 함수를 가져와도 됨
            fetch(`http://localhost:8000/api/stock/news/${query}`)
                .then(res => res.json())
                .then(data => {
                    setNews(data);
                    setLoading(false);
                })
                .catch(err => {
                    console.error("News fetch failed:", err);
                    setLoading(false);
                });
        }
    }, [opened, stockName]);

    return (
        <Drawer
            opened={opened}
            onClose={onClose}
            title={
                <Group>
                    <IconNews size={20} />
                    <Text fw={700}>{stockName} 관련 뉴스</Text>
                </Group>
            }
            position="right"
            size="md"
            padding="md"
            styles={{
                content: {
                    background: 'rgba(28, 28, 30, 0.95)',
                    backdropFilter: 'blur(10px)',
                    color: '#fff',
                },
                header: {
                    background: 'transparent',
                    color: '#fff',
                },
                close: {
                    color: '#fff',
                    '&:hover': { background: 'rgba(255,255,255,0.1)' }
                }
            }}
        >
            <ScrollArea h="calc(100vh - 80px)">
                {loading ? (
                    <Center h={200}>
                        <Loader variant="bars" color="blue" />
                    </Center>
                ) : news.length > 0 ? (
                    <Stack gap="md">
                        {news
                            .filter(item => {
                                try {
                                    // 날짜 파싱 (YYYY.MM.DD HH:MM or similar)
                                    // 3일 전 기준
                                    const dateStr = item.date.replace(/\./g, '-');
                                    const newsDate = new Date(dateStr);
                                    const threeDaysAgo = new Date();
                                    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
                                    return newsDate >= threeDaysAgo;
                                } catch (e) {
                                    return true; // 파싱 실패시 일단 표시
                                }
                            })
                            .map((item, index) => (
                                <Card
                                    key={index}
                                    withBorder
                                    shadow="sm"
                                    radius="md"
                                    component="a"
                                    href={item.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="hover:bg-white/5 transition-colors"
                                    style={{
                                        background: 'rgba(255,255,255,0.05)',
                                        borderColor: 'rgba(255,255,255,0.1)',
                                        color: 'white'
                                    }}
                                >
                                    <Text size="sm" fw={600} mb="xs" lineClamp={2} c="white">
                                        {item.title}
                                    </Text>
                                    <Group justify="space-between">
                                        <Text size="xs" c="dimmed">
                                            {item.source}
                                        </Text>
                                        <Text size="xs" c="dimmed">
                                            {item.date}
                                        </Text>
                                    </Group>
                                </Card>
                            ))}
                    </Stack>
                ) : (
                    <Center h={100}>
                        <Text c="dimmed">관련 뉴스가 없습니다.</Text>
                    </Center>
                )}
            </ScrollArea>
        </Drawer>
    );
}
