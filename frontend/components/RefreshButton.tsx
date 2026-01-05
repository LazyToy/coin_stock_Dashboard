"use client";

import { Button, Tooltip, Menu, Text, Group } from "@mantine/core";
import { IconRefresh, IconClock, IconCheck } from "@tabler/icons-react";
import { useState, useEffect, useCallback } from "react";

interface RefreshButtonProps {
    onRefresh: () => Promise<void>;
    loading: boolean;
    lastUpdated: string | null;
}

export function RefreshButton({ onRefresh, loading, lastUpdated }: RefreshButtonProps) {
    const [cooldown, setCooldown] = useState(false);
    const [autoRefresh, setAutoRefresh] = useState<number | null>(null);
    const [timeAgo, setTimeAgo] = useState<string>("");

    // 시간 경과 계산
    const updateTimeAgo = useCallback(() => {
        if (!lastUpdated) {
            setTimeAgo("");
            return;
        }

        const now = new Date();
        const updated = new Date(lastUpdated);
        const diffSeconds = Math.floor((now.getTime() - updated.getTime()) / 1000);

        if (diffSeconds < 60) {
            setTimeAgo(`${diffSeconds}초 전`);
        } else if (diffSeconds < 3600) {
            setTimeAgo(`${Math.floor(diffSeconds / 60)}분 전`);
        } else {
            setTimeAgo(`${Math.floor(diffSeconds / 3600)}시간 전`);
        }
    }, [lastUpdated]);

    // 매초 시간 경과 업데이트
    useEffect(() => {
        updateTimeAgo();
        const interval = setInterval(updateTimeAgo, 1000);
        return () => clearInterval(interval);
    }, [updateTimeAgo]);

    // 자동 새로고침
    useEffect(() => {
        if (!autoRefresh) return;

        const interval = setInterval(() => {
            handleRefresh();
        }, autoRefresh * 1000);

        return () => clearInterval(interval);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [autoRefresh]);

    const handleRefresh = async () => {
        if (cooldown || loading) return;

        try {
            await onRefresh();
            setCooldown(true);
            // 5초 쿨다운
            setTimeout(() => setCooldown(false), 5000);
        } catch (error) {
            console.error("Refresh failed:", error);
        }
    };

    const autoRefreshOptions = [
        { label: "자동 새로고침 끄기", value: null },
        { label: "30초마다", value: 30 },
        { label: "1분마다", value: 60 },
        { label: "5분마다", value: 300 },
    ];

    return (
        <Group gap="sm">
            {/* 마지막 업데이트 시간 */}
            {timeAgo && (
                <Tooltip label="마지막 업데이트 시간">
                    <Group gap={4} style={{ opacity: 0.7 }}>
                        <IconClock size={14} />
                        <Text size="xs" c="dimmed">
                            {timeAgo}
                        </Text>
                    </Group>
                </Tooltip>
            )}

            {/* 자동 새로고침 메뉴 */}
            <Menu shadow="md" width={200}>
                <Menu.Target>
                    <Button
                        variant="subtle"
                        size="xs"
                        color={autoRefresh ? "green" : "gray"}
                    >
                        {autoRefresh ? `${autoRefresh}초` : "자동"}
                    </Button>
                </Menu.Target>
                <Menu.Dropdown>
                    <Menu.Label>자동 새로고침 설정</Menu.Label>
                    {autoRefreshOptions.map((option) => (
                        <Menu.Item
                            key={option.value ?? "off"}
                            leftSection={
                                autoRefresh === option.value ? (
                                    <IconCheck size={14} />
                                ) : null
                            }
                            onClick={() => setAutoRefresh(option.value)}
                        >
                            {option.label}
                        </Menu.Item>
                    ))}
                </Menu.Dropdown>
            </Menu>

            {/* 새로고침 버튼 */}
            <Tooltip label={cooldown ? "잠시 후 다시 시도해주세요" : "데이터 새로고침"}>
                <Button
                    variant="gradient"
                    gradient={{ from: "violet", to: "grape", deg: 135 }}
                    leftSection={
                        <IconRefresh
                            size={18}
                            style={{
                                animation: loading ? "spin 1s linear infinite" : "none",
                            }}
                        />
                    }
                    onClick={handleRefresh}
                    loading={loading}
                    disabled={cooldown}
                    styles={{
                        root: {
                            transition: "all 0.3s ease",
                            "&:hover": {
                                transform: "scale(1.02)",
                            },
                        },
                    }}
                >
                    새로고침
                </Button>
            </Tooltip>

            <style jsx global>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
        </Group>
    );
}
