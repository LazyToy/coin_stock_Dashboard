"use client";

import { useState, useEffect, useCallback } from "react";
import {
    AppShell,
    Container,
    Title,
    Group,
    Text,
    Button,
    Grid,
    SimpleGrid,
    Stack,
    ThemeIcon,
    Alert,
    Center,
    Loader,
    Paper,
    Badge,
    SegmentedControl,
} from "@mantine/core";
import { useDisclosure } from '@mantine/hooks';
import { notifications } from "@mantine/notifications";
import {
    IconCurrencyBitcoin,
    IconChartLine,
    IconAlertCircle,
    IconRocket,
    IconBuildingSkyscraper,
    IconChartBar,
} from "@tabler/icons-react";
import { DashboardData, StockDashboardData } from "@/types/api";
import { fetchDashboard, fetchStockDashboard } from "@/utils/api";
import { BalanceCard } from "./BalanceCard";
import { HoldingsTable } from "./HoldingsTable";
import { TopVolumeTable } from "./TopVolumeTable";
import { StockVolumeTable } from "./StockVolumeTable";
import { RefreshButton } from "./RefreshButton";
import { StockIndicesCard } from "./StockIndicesCard";
import { SectorHeatmap } from "./SectorHeatmap";
import { StockNewsDrawer } from "./StockNewsDrawer";
import { FearGreedCard } from "./FearGreedCard";
import { WhaleAlertCard } from "./WhaleAlertCard";
import { EtfTable } from "./EtfTable";

type ViewMode = "crypto" | "stock";

export function Dashboard() {
    const [viewMode, setViewMode] = useState<ViewMode>("crypto");
    const [cryptoData, setCryptoData] = useState<DashboardData | null>(null);
    const [stockData, setStockData] = useState<StockDashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // News Drawer State
    const [newsOpened, { open: openNews, close: closeNews }] = useDisclosure(false);
    const [selectedStock, setSelectedStock] = useState<string | null>(null);

    const handleStockClick = (name: string) => {
        setSelectedStock(name);
        openNews();
    };

    const loadCryptoData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await fetchDashboard();
            setCryptoData(result);
            notifications.show({
                title: "암호화폐 데이터 업데이트",
                message: "최신 데이터를 불러왔습니다",
                color: "green",
                autoClose: 2000,
            });
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "데이터를 불러오는데 실패했습니다";
            setError(errorMessage);
            notifications.show({
                title: "오류 발생",
                message: errorMessage,
                color: "red",
            });
        } finally {
            setLoading(false);
        }
    }, []);

    const loadStockData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await fetchStockDashboard();
            setStockData(result);
            notifications.show({
                title: "주식 데이터 업데이트",
                message: "최신 데이터를 불러왔습니다",
                color: "green",
                autoClose: 2000,
            });
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "데이터를 불러오는데 실패했습니다";
            setError(errorMessage);
            notifications.show({
                title: "오류 발생",
                message: errorMessage,
                color: "red",
            });
        } finally {
            setLoading(false);
        }
    }, []);

    const loadData = useCallback(async () => {
        if (viewMode === "crypto") {
            await loadCryptoData();
        } else {
            await loadStockData();
        }
    }, [viewMode, loadCryptoData, loadStockData]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleViewModeChange = (value: string) => {
        setViewMode(value as ViewMode);
    };

    const currentData = viewMode === "crypto" ? cryptoData : stockData;

    return (
        <AppShell
            header={{ height: 80 }}
            padding="md"
            styles={{
                header: {
                    background: "rgba(26, 27, 30, 0.8)",
                    backdropFilter: "blur(10px)",
                    borderBottom: "1px solid rgba(255,255,255,0.1)",
                },
                main: {
                    background: "transparent",
                },
            }}
        >
            {/* Header */}
            <AppShell.Header style={{ background: "rgba(0, 0, 0, 0.7)", borderBottom: "1px solid rgba(255, 255, 255, 0.1)", backdropFilter: "blur(20px)" }}>
                <Container size="xl" h="100%">
                    <Group justify="space-between" align="center" h="100%">
                        <Group align="center" gap="sm">
                            <ThemeIcon size={42} radius="md" variant="gradient" gradient={{ from: '#0A84FF', to: '#5E5CE6' }}>
                                {viewMode === "crypto" ? <IconCurrencyBitcoin size={24} color="white" /> : <IconChartBar size={24} color="white" />}
                            </ThemeIcon>
                            <Stack gap={0}>
                                <Title order={2} style={{ color: '#FFF', fontSize: 22, fontWeight: 700 }}>
                                    {viewMode === "crypto" ? "Crypto Dashboard" : "Stock Dashboard"}
                                </Title>
                                <Text size="xs" c="dimmed">Real-time Portfolio Tracker</Text>
                            </Stack>
                        </Group>

                        <Group gap="md">
                            <SegmentedControl
                                value={viewMode}
                                onChange={(value) => setViewMode(value as "crypto" | "stock")}
                                data={[
                                    { label: "Crypto Asset", value: "crypto" },
                                    { label: "Stock Market", value: "stock" },
                                ]}
                                size="md"
                                radius="xl"
                                withItemsBorders={false}
                                style={{
                                    background: 'rgba(255, 255, 255, 0.1)',
                                    backdropFilter: 'blur(10px)',
                                    border: '1px solid rgba(255, 255, 255, 0.1)'
                                }}
                                styles={{
                                    root: { backgroundColor: 'transparent' },
                                    indicator: { backgroundColor: '#0A84FF', boxShadow: '0 0 15px rgba(10, 132, 255, 0.5)' },
                                    label: { color: '#86868B', fontWeight: 600, fontSize: 13 },
                                }}
                            />

                            <RefreshButton
                                onRefresh={loadData}
                                loading={loading}
                                lastUpdated={currentData?.last_updated || null}
                            />
                        </Group>
                    </Group>
                </Container>
            </AppShell.Header>

            {/* Main Content */}
            <AppShell.Main>
                <Container size="xl" py="xl">
                    {/* Error Alert */}
                    {error && (
                        <Alert
                            icon={<IconAlertCircle size={20} />}
                            title="연결 오류"
                            color="red"
                            mb="xl"
                            variant="filled"
                        >
                            {error}
                            <Text size="sm" mt="xs">
                                백엔드 서버가 실행 중인지 확인해주세요. (http://localhost:8000)
                            </Text>
                        </Alert>
                    )}

                    {/* Initial Loading */}
                    {loading && !currentData && (
                        <Center h={400}>
                            <Stack align="center" gap="md">
                                <Loader size="xl" color="violet" />
                                <Text c="dimmed">데이터를 불러오는 중...</Text>
                            </Stack>
                        </Center>
                    )}

                    {/* Crypto Dashboard Content */}
                    {viewMode === "crypto" && cryptoData && (
                        <Stack gap="xl">
                            {/* Total Overview */}
                            {/* Total Overview */}
                            {/* Total Overview Hero */}
                            <Paper
                                className="glass-card animate-fadeIn"
                                p="xl"
                                radius="lg"
                                style={{
                                    background: 'linear-gradient(180deg, rgba(30,30,40,0.8) 0%, rgba(20,20,25,0.6) 100%)',
                                    border: '1px solid rgba(255,255,255,0.1)'
                                }}
                            >
                                <Stack gap="xs" align="center" py="md">
                                    <Text size="sm" c="dimmed" tt="uppercase" fw={700} style={{ letterSpacing: 2 }}>
                                        Crypto Portfolio
                                    </Text>
                                    <Title order={1} style={{ fontSize: 48, fontWeight: 800, color: '#fff' }}>
                                        Digital Assets
                                    </Title>
                                    <Text c="dimmed">Real-time Upbit & Binance Integration</Text>
                                </Stack>
                            </Paper>

                            {/* Balance Cards */}
                            {/* Balance Cards */}
                            <Grid gutter="lg">
                                <Grid.Col span={{ base: 12, md: 6 }}>
                                    <BalanceCard
                                        exchange="upbit"
                                        total={cryptoData.upbit_balance?.total_krw || 0}
                                        available={cryptoData.upbit_balance?.available_krw || 0}
                                        locked={cryptoData.upbit_balance?.locked_krw || 0}
                                        loading={loading}
                                    />
                                </Grid.Col>
                                <Grid.Col span={{ base: 12, md: 6 }}>
                                    <BalanceCard
                                        exchange="binance"
                                        total={cryptoData.binance_balance?.total_usdt || 0}
                                        available={cryptoData.binance_balance?.available_usdt || 0}
                                        locked={cryptoData.binance_balance?.locked_usdt || 0}
                                        loading={loading}
                                    />
                                </Grid.Col>
                            </Grid>

                            {/* Fear & Greed AND Whale Alerts */}
                            <Grid gutter="lg" align="stretch">
                                <Grid.Col span={{ base: 12, md: 4 }}>
                                    <FearGreedCard data={cryptoData.fear_greed} />
                                </Grid.Col>
                                <Grid.Col span={{ base: 12, md: 8 }}>
                                    <WhaleAlertCard alerts={cryptoData.whale_alerts} />
                                </Grid.Col>
                            </Grid>

                            {/* Holdings Tables */}
                            {/* Holdings Tables */}
                            <Grid gutter="lg">
                                <Grid.Col span={{ base: 12, lg: 6 }}>
                                    <HoldingsTable
                                        exchange="upbit"
                                        holdings={cryptoData.upbit_holdings}
                                        loading={loading}
                                    />
                                </Grid.Col>
                                <Grid.Col span={{ base: 12, lg: 6 }}>
                                    <HoldingsTable
                                        exchange="binance"
                                        holdings={cryptoData.binance_holdings}
                                        loading={loading}
                                    />
                                </Grid.Col>
                            </Grid>

                            {/* Top Volume Tables */}
                            {/* Top Volume Tables */}
                            <Grid gutter="lg">
                                <Grid.Col span={{ base: 12, lg: 6 }}>
                                    <TopVolumeTable
                                        exchange="upbit"
                                        coins={cryptoData.upbit_top_volume}
                                        loading={loading}
                                    />
                                </Grid.Col>
                                <Grid.Col span={{ base: 12, lg: 6 }}>
                                    <TopVolumeTable
                                        exchange="binance"
                                        coins={cryptoData.binance_top_volume}
                                        loading={loading}
                                    />
                                </Grid.Col>
                            </Grid>
                        </Stack>
                    )}

                    {/* Stock Dashboard Content */}
                    {viewMode === "stock" && stockData && (
                        <Stack gap="xl">
                            {/* Stock Overview */}
                            {/* Stock Overview */}
                            {/* Stock Overview Hero */}
                            <Paper
                                className="glass-card animate-fadeIn"
                                p="xl"
                                radius="lg"
                                style={{
                                    background: 'linear-gradient(180deg, rgba(30,30,40,0.8) 0%, rgba(20,20,25,0.6) 100%)',
                                    border: '1px solid rgba(255,255,255,0.1)'
                                }}
                            >
                                <Stack gap="xs" align="center" py="md">
                                    <Text size="sm" c="dimmed" tt="uppercase" fw={700} style={{ letterSpacing: 2 }}>
                                        Global Markets
                                    </Text>
                                    <Title order={1} style={{ fontSize: 48, fontWeight: 800, color: '#fff' }}>
                                        Stock & ETF
                                    </Title>
                                    <Text c="dimmed">KOSPI • KOSDAQ • NASDAQ • S&P 500</Text>
                                </Stack>
                            </Paper>

                            {/* Major Indices */}
                            <StockIndicesCard indices={stockData.indices} />

                            {/* Sector Heatmap */}
                            <SectorHeatmap sectors={stockData.sectors} />

                            <Grid gutter="lg">
                                <Grid.Col span={{ base: 12, lg: 6 }}>
                                    <StockVolumeTable
                                        market="us"
                                        stocks={stockData.us_top}
                                        loading={loading}
                                        onStockClick={handleStockClick}
                                    />
                                </Grid.Col>
                                <Grid.Col span={{ base: 12, lg: 6 }}>
                                    <EtfTable
                                        etfs={stockData.etf_ranking}
                                        loading={loading}
                                    />
                                </Grid.Col>
                                <Grid.Col span={{ base: 12, lg: 6 }}>
                                    <StockVolumeTable
                                        market="kospi"
                                        stocks={stockData.kospi_top}
                                        loading={loading}
                                        onStockClick={handleStockClick}
                                    />
                                </Grid.Col>
                                <Grid.Col span={{ base: 12, lg: 6 }}>
                                    <StockVolumeTable
                                        market="kosdaq"
                                        stocks={stockData.kosdaq_top}
                                        loading={loading}
                                        onStockClick={handleStockClick}
                                    />
                                </Grid.Col>
                            </Grid>
                        </Stack>
                    )}
                </Container>
            </AppShell.Main>

            <StockNewsDrawer
                opened={newsOpened}
                onClose={closeNews}
                stockName={selectedStock}
            />
        </AppShell >
    );
}
